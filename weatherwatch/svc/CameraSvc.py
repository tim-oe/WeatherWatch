import logging
import shutil

import piexif
from camera.Camera import Camera
from conf.AppConfig import AppConfig
from conf.CameraConfig import CameraConfig
from conf.GPSConfig import GPSConfig
from entity.OutdoorSensor import OutdoorSensor
from gps.DMSCoordinate import DMSCoordinate
from gps.GPSData import GPSData
from gps.GPSReader import GPSReader
from py_singleton import singleton
from pytemp import pytemp
from repository.OutdoorSensorRepository import OutdoorSensorRepository

__all__ = ["CameraSvc"]


@singleton
class CameraSvc:
    """
    camera service
    this does camera processing
    1) get lux for low light optimization
    2) take pic
    3) copy to current
    """

    GPS_ACCURACY = 10**6

    def __init__(self):
        self.camera: Camera = Camera()
        self._cameraConfig: CameraConfig = AppConfig().camera
        self._gpsConfig: GPSConfig = AppConfig().gps
        self._repo: OutdoorSensorRepository = OutdoorSensorRepository()

    def process(self):
        logging.info("processing camera")
        data: OutdoorSensor = self._repo.findLatest()

        try:
            imgFile: str = self.camera.process(data.light_lux)

            self.addCustomExif(imgFile, data)

            shutil.copy(imgFile, self._cameraConfig.currentFile)
        except Exception:
            logging.exception("failed to take picture")

    def addCustomExif(self, image_path, data: OutdoorSensor):
        """
        add custom exif metadata
        https://exiftool.org/TagNames/EXIF.html
        https://exiftool.org/TagNames/GPS.html
        https://stackoverflow.com/questions/76421934/adding-gps-location-to-exif-using-python-slots-not-recognised-by-windows-10-n
        """
        try:
            # Load the Exif data
            exif_dict = piexif.load(image_path)

            # Add custom metadata to the Exif UserComment
            c = pytemp(float(data.temperature_f), "f", "c")

            # TODO proper value?
            # exif_dict["0th"][piexif.ImageIFD.DocumentName] = "local weather"

            # daylight
            exif_dict["Exif"][piexif.ExifIFD.LightSource] = 1
            exif_dict["Exif"][piexif.ExifIFD.BrightnessValue] = (int(data.light_lux), 1)

            exif_dict["Exif"][piexif.ExifIFD.LensMake] = self._cameraConfig.lensMake
            exif_dict["Exif"][piexif.ExifIFD.LensModel] = self._cameraConfig.lensModel

            # weather
            exif_dict["Exif"][piexif.ExifIFD.Temperature] = (int(c), 1)
            exif_dict["Exif"][piexif.ExifIFD.Humidity] = (data.humidity, 100)
            exif_dict["Exif"][piexif.ExifIFD.Pressure] = (int(data.pressure), 1)

            self.addGPSExif(exif_dict)

            # TODO what other data
            # exif_dict["Exif"][piexif.ExifIFD.UserComment]

            # Dump the modified Exif data
            exif_bytes = piexif.dump(exif_dict)

            # Save the image with the new Exif data
            piexif.insert(exif_bytes, image_path)
        except Exception:
            logging.exception("failed to set exif data")

    def addGPSExif(self, exif_dict):
        if self._gpsConfig.enable is True:
            gpsReader: GPSReader = GPSReader()
            data: GPSData = gpsReader.read()
            lat: DMSCoordinate = data.latitudeDMS
            logging.debug(f"latitudeDMS {data.latitudeDMS}")

            lon: DMSCoordinate = data.longitudeDMS
            logging.debug(f"longitudeDMS {data.longitudeDMS}")

            logging.debug(f"altitude {data.altitude}")
            # seen issue with value being not set and taking cycles to become accurate
            if data.altitude is not None and data.altitude > 0:
                exif_dict["GPS"][piexif.GPSIFD.GPSAltitude] = (int(data.altitude), 1)
                # above see level
                exif_dict["GPS"][piexif.GPSIFD.GPSAltitudeRef] = 0

            exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] = [
                (int(lat.degrees), 1),
                (int(lat.minutes), 1),
                (int(lat.seconds * CameraSvc.GPS_ACCURACY), CameraSvc.GPS_ACCURACY),
            ]
            exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = lat.ordinal.value
            exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] = [
                (int(lon.degrees), 1),
                (int(lon.minutes), 1),
                (int(lon.seconds * CameraSvc.GPS_ACCURACY), CameraSvc.GPS_ACCURACY),
            ]
            exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = lon.ordinal.value
