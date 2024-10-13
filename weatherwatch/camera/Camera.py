import datetime
import logging
import time
from pathlib import Path

from conf.AppConfig import AppConfig
from conf.CameraConfig import CameraConfig
from picamera2 import Picamera2, Preview
from picamera2.allocators import PersistentAllocator
from py_singleton import singleton


@singleton
class Camera:
    """
    encapsulates camera functionality
    lib: https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf
    software: https://www.raspberrypi.com/documentation/computers/camera_software.html#rpicam-apps
    examples: https://github.com/raspberrypi/picamera2/tree/main/examples
    tuning: https://forums.raspberrypi.com/viewtopic.php?t=351189
    cli (for noir cam): libcamera-still --tuning-file /usr/share/libcamera/ipa/rpi/vc4/imx219_noir.json  --output preview.jpg
    """  # noqa

    def __init__(self):
        """
        ctor
        :param self: this
        """

        self._cameraConfig: CameraConfig = AppConfig().camera

        self._baseDir: Path = self._cameraConfig.folder

        self._baseDir.mkdir(parents=True, exist_ok=True)

        tuning = None
        if self._cameraConfig.tuningEnable is True:
            tuning = Picamera2.load_tuning_file(self._cameraConfig.tuningFile)

        self._picam2 = Picamera2(tuning=tuning, allocator=PersistentAllocator())

    # override
    def __del__(self):
        self._picam2.close()

    @property
    def enable(self) -> bool:
        """
        enable property getter
        :param self: this
        :return: the enable
        """
        return self._cameraConfig.enable

    def process(self):
        if self._cameraConfig.enable is False:
            logging.debug("camera not enabled")
            return

        try:
            self._picam2.start_preview(Preview.NULL)

            preview_config = self._picam2.create_preview_configuration()
            self._picam2.configure(preview_config)

            self._picam2.start()
            # TODO is this needed?
            time.sleep(2)

            capture_config = self._picam2.create_still_configuration()
            self._picam2.switch_mode_and_capture_file(capture_config, self.imageFile())

            # TODO is this needed?
            time.sleep(2)
        except Exception:
            logging.exception("failed to take pic...")
        finally:
            self._picam2.stop_preview()
            self._picam2.stop()

    def imageFile(self) -> str:
        now = datetime.datetime.now()

        imageName = now.strftime("%Y-%m-%d-%H-%M-%S") + self._cameraConfig.extension

        return str(self._baseDir / imageName)
