import datetime
import time
from pathlib import Path

from conf.AppConfig import AppConfig
from conf.CameraConfig import CameraConfig
from picamera2 import Picamera2, Preview
from picamera2.allocators import PersistentAllocator
from py_singleton import singleton
from util.Logger import logger


@logger
@singleton
class Camera:
    """
    encapsulates camera functionality
    lib: https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf
    software: https://www.raspberrypi.com/documentation/computers/camera_software.html#rpicam-apps
    examples: https://github.com/raspberrypi/picamera2/tree/main/examples
    tuning: https://forums.raspberrypi.com/viewtopic.php?t=351189
    cli (for noir cam): libcamera-still --tuning-file /usr/share/libcamera/ipa/rpi/vc4/imx219_noir.json  --output preview.jpg
    TODO: https://github.com/raspberrypi/picamera2/issues/239
    work around: https://rockyshikoku.medium.com/use-h264-codec-with-cv2-videowriter-e00145ded181
    """  # noqa

    # second to micro second multiplier
    MICRO_SECOND: int = 1000000

    def __init__(self):
        """
        ctor
        :param self: this
        """

        # https://forums.raspberrypi.com/viewtopic.php?t=364677
        # default logging is warn
        Picamera2.set_logging()

        self._cameraConfig: CameraConfig = AppConfig().camera

        self._baseDir: Path = self._cameraConfig.folder

        self._baseDir.mkdir(parents=True, exist_ok=True)

        tuning = None
        if self._cameraConfig.tuningEnable is True:
            tuning = Picamera2.load_tuning_file(self._cameraConfig.tuningFile)

        self._picam2 = Picamera2(tuning=tuning, allocator=PersistentAllocator())

    def process(self, lux: int) -> str:
        if self._cameraConfig.enable is False:
            self.logger.debug("camera not enabled")
            return

        try:
            self._picam2.start_preview(Preview.NULL)

            # TODO is this needed?
            time.sleep(1)

            preview_config = self._picam2.create_preview_configuration()
            self._picam2.configure(preview_config)

            controls = {}
            if lux <= self._cameraConfig.luxLimit:
                controls = {
                    "ExposureTime": (self._cameraConfig.exposureTime * Camera.MICRO_SECOND),
                    "AnalogueGain": self._cameraConfig.analogueGain,
                }
            else:  # clear controls https://github.com/raspberrypi/picamera2/issues/1175
                controls = {
                    "ExposureTime": 0,
                    "AnalogueGain": 0,
                }

            self._picam2.start()

            time.sleep(1)

            imgFile: str = self.imageFile()
            capture_config = self._picam2.create_still_configuration(controls=controls)
            # TODO inject exif data here
            self._picam2.switch_mode_and_capture_file(capture_config, imgFile, wait=True)

            return imgFile
        except Exception as e:
            self.logger.exception("failed to take pic...")
            raise Exception("failed to take pic...") from e
        finally:
            self._picam2.stop_preview()
            self._picam2.stop()
            # self._picam2.close()

    def imageFile(self) -> str:
        now = datetime.datetime.now()

        stamp = now.strftime("%Y-%m-%d-%H-%M-%S")
        imageName = f"{stamp}{self._cameraConfig.extension}"

        return str(self._baseDir / imageName)
