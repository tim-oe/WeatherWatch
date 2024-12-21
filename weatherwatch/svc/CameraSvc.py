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
from util.Logger import logger

__all__ = ["CameraSvc"]


@logger
@singleton
class CameraSvc:
    """
    camera service
    this does camera processing
    1) get lux for low light optimization
    2) take pic
    3) add exif data
    4) copy to current
    """

    # buried in a subcomment how to add addtional accuracy to exif gps data
    # https://stackoverflow.com/questions/76421934/adding-gps-location-to-exif-using-python-slots-not-recognised-by-windows-10-n
    GPS_ACCURACY = 10**6

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self.camera: Camera = Camera()
        self._camera_config: CameraConfig = AppConfig().camera
        self._gps_config: GPSConfig = AppConfig().gps
        self._repo: OutdoorSensorRepository = OutdoorSensorRepository()

    def process(self):
        """
        main service entry point
        :param self: this
        """
        self.logger.info("processing camera")
        data: OutdoorSensor = self._repo.find_latest()

        try:
            img_file: str = self.camera.process(data.light_lux)

            self.add_custom_exif(img_file, data)

            shutil.copy(img_file, self._camera_config.current_file)
        except Exception:
            self.logger.exception("failed to take picture")

    def add_custom_exif(self, image_path, data: OutdoorSensor):
        """
        add custom exif metadata
        :param self: this
        :param image_path: the path to the image
        :param data: the sensor data to add to image
        TODO need to look at camera2 lib as there's hooks to add at snapshot
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

            exif_dict["Exif"][piexif.ExifIFD.LensMake] = self._camera_config.lens_make
            exif_dict["Exif"][piexif.ExifIFD.LensModel] = self._camera_config.lens_model

            # weather
            exif_dict["Exif"][piexif.ExifIFD.Temperature] = (int(c), 1)
            exif_dict["Exif"][piexif.ExifIFD.Humidity] = (data.humidity, 100)
            exif_dict["Exif"][piexif.ExifIFD.Pressure] = (int(data.pressure), 1)

            self.add_gps_exif(exif_dict)

            # TODO what other data
            # exif_dict["Exif"][piexif.ExifIFD.UserComment]

            # Dump the modified Exif data
            exif_bytes = piexif.dump(exif_dict)

            # Save the image with the new Exif data
            piexif.insert(exif_bytes, image_path)
        except Exception:
            self.logger.exception("failed to set exif data")

    def add_gps_exif(self, exif_dict):
        """
        add gps exif metadata
        :param self: this
        :param exif_dict: the image exif data dictionary
        """
        if self._gps_config.enable is True:
            gps_reader: GPSReader = GPSReader()
            data: GPSData = gps_reader.read()
            lat: DMSCoordinate = data.latitude_dms
            self.logger.debug(f"latitudeDMS {data.latitude_dms}")

            lon: DMSCoordinate = data.longitude_dms
            self.logger.debug(f"longitudeDMS {data.longitude_dms}")

            self.logger.debug(f"altitude {data.altitude}")
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
