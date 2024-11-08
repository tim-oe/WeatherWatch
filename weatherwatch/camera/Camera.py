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

    def process(self, lux: int) -> str:
        if self._cameraConfig.enable is False:
            logging.debug("camera not enabled")
            return

        try:
            tuning = None
            if self._cameraConfig.tuningEnable is True:
                tuning = Picamera2.load_tuning_file(self._cameraConfig.tuningFile)

            picam2 = Picamera2(tuning=tuning, allocator=PersistentAllocator())

            # TODO is this needed?
            time.sleep(1)

            picam2.start_preview(Preview.NULL)

            preview_config = picam2.create_preview_configuration()
            picam2.configure(preview_config)

            if lux < self._cameraConfig.luxLimit:
                picam2.set_controls(
                    {
                        "ExposureTime": (self._cameraConfig.exposureTime * Camera.MICRO_SECOND),
                        "AnalogueGain": self._cameraConfig.analogueGain,
                    }
                )

            picam2.start()
            # TODO is this needed?
            time.sleep(1)

            imgFile: str = self.imageFile()
            capture_config = picam2.create_still_configuration()
            picam2.switch_mode_and_capture_file(capture_config, imgFile, wait=True)

            return imgFile
        except Exception as e:
            raise Exception("failed to take pic...") from e
        finally:
            picam2.stop_preview()
            picam2.stop()
            picam2.close()

    def imageFile(self) -> str:
        now = datetime.datetime.now()

        stamp = now.strftime("%Y-%m-%d-%H-%M-%S")
        imageName = f"{stamp}{self._cameraConfig.extension}"

        return str(self._baseDir / imageName)
