import time
from datetime import datetime
from pathlib import Path

import libcamera
from conf.AppConfig import AppConfig
from conf.CameraConfig import CameraConfig
from picamera2 import Picamera2, Preview
from picamera2.allocators import PersistentAllocator
from py_singleton import singleton
from util.Emailer import Emailer
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

        self._camera_config: CameraConfig = AppConfig().camera

        self._emailer = Emailer()

        self._base_dir: Path = self._camera_config.folder

        self._base_dir.mkdir(parents=True, exist_ok=True)

        tuning = None
        if self._camera_config.tuning_enable is True:
            tuning = Picamera2.load_tuning_file(self._camera_config.tuning_file)

        self._picam2 = Picamera2(tuning=tuning, allocator=PersistentAllocator())

    def process(self, lux: int) -> str | None:
        """
        camera processing entry point
        :param self: this
        :param lux: the ambient light level to contol exposure/iso settings
        :returns image path
        """
        if self._camera_config.enable is False:
            self.logger.debug("camera not enabled")
            return None

        try:
            self._picam2.start_preview(Preview.NULL)

            # TODO is this needed?
            time.sleep(1)

            preview_config = self._picam2.create_preview_configuration()
            self._picam2.configure(preview_config)

            controls = {}
            if lux <= self._camera_config.lux_limit:
                controls = {
                    "ExposureTime": (self._camera_config.exposure_time * Camera.MICRO_SECOND),
                    "AnalogueGain": self._camera_config.analogue_gain,
                    "NoiseReductionMode": libcamera.controls.draft.NoiseReductionModeEnum.HighQuality,
                    "AwbEnable": True,
                    "AwbMode": libcamera.controls.AwbModeEnum.Auto,
                    "AeEnable": False,  # Disable auto exposure
                    "Brightness": 0.1,  # Slight brightness boost
                    "Contrast": 1.2,  # Increase contrast
                    "Saturation": 1.1,  # Slight saturation boost
                    "Sharpness": 1.0,  # Maintain sharpness
                }
            else:  # clear controls https://github.com/raspberrypi/picamera2/issues/1175
                controls = {
                    "ExposureTime": 0,
                    "AnalogueGain": 0,
                    "AwbEnable": True,
                    "AwbMode": libcamera.controls.AwbModeEnum.Daylight,
                    "AeEnable": True,
                    "Brightness": 0.0,
                    "Contrast": 1.0,
                    "Saturation": 1.0,
                    "Sharpness": 1.0,
                }

            self._picam2.start()

            time.sleep(1)

            img_file: str = self.image_file()
            capture_config = self._picam2.create_still_configuration(controls=controls)
            # default=lambda obj: obj.to_dict()
            self.logger.info("capture config %s", capture_config)

            # from docs fishing for fix...
            self._picam2.set_controls(controls)

            # TODO inject exif data here
            self._picam2.switch_mode_and_capture_file(capture_config, img_file, wait=True)

            return img_file
        except Exception as e:
            self._emailer.send_error_notification(e, subject_prefix="failed to take pic")
        finally:
            self._picam2.stop_preview()
            self._picam2.stop()
            # self._picam2.close()

    def image_file(self) -> str:
        """
        build image file name including path
        :param self: this
        :returns image file name including path
        """

        now = datetime.now()

        stamp = now.strftime("%Y-%m-%d-%H-%M-%S")
        image_name = f"{stamp}{self._camera_config.extension}"

        return str(self._base_dir / image_name)
