import datetime
import json
import logging
import shutil

import piexif
from camera.Camera import Camera
from conf.AppConfig import AppConfig
from conf.CameraConfig import CameraConfig
from entity.OutdoorSensor import OutdoorSensor
from py_singleton import singleton
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

    def __init__(self):
        self.camera: Camera = Camera()
        self._config: CameraConfig = AppConfig().camera
        self._repo: OutdoorSensorRepository = OutdoorSensorRepository()

    def process(self):
        logging.info("processing camera")
        data: OutdoorSensor = self._repo.findLatest()

        try:
            imgFile: str = self.camera.process(data.light_lux)

            shutil.copy(imgFile, self._config.currentFile)

        except Exception:
            logging.exception("failed to take picture")

    def addCustomExif(self, image_path, metadata):
        """
        add custom exif metadata
        https://github.com/raspberrypi/picamera2/issues/674
        https://stackoverflow.com/questions/76421934/adding-gps-location-to-exif-using-python-slots-not-recognised-by-windows-10-n
        """
        # Load the Exif data
        exif_dict = piexif.load(image_path)

        # Add custom metadata to the Exif UserComment
        exif_dict["Exif"][piexif.ExifIFD.UserComment] = json.dumps(metadata).encode("utf-8")

        # Dump the modified Exif data
        exif_bytes = piexif.dump(exif_dict)

        # Save the image with the new Exif data
        piexif.insert(exif_bytes, image_path)

    def imageFile(self) -> str:
        now = datetime.datetime.now()

        stamp = now.strftime("%Y-%m-%d-%H-%M-%S")
        imageName = f"{stamp}{self._cameraConfig.extension}"

        return str(self._baseDir / imageName)
