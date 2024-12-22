from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List

# AI tells me
# pylint: disable=no-member, invalid-name
import cv2
from conf.AppConfig import AppConfig
from conf.CameraConfig import CameraConfig
from conf.TimelapseConfig import TimelapseConfig
from py_singleton import singleton
from util.Converter import Converter
from util.Logger import logger


@logger
@singleton
class Timelapse:
    """
    makes timelapse video out for images taken by camera
    uses opencv with h264 encoding as the default
    requires non binary distro to use codec due to lic
    this is memory intensive so won't work on a pi zero
    """  # noqa

    def __init__(self):
        """
        ctor
        :param self: this
        """

        self._camera_config: CameraConfig = AppConfig().camera
        self._timelapse_config: TimelapseConfig = AppConfig().timelapse

        self._base_dir: Path = self._timelapse_config.folder

        self._base_dir.mkdir(parents=True, exist_ok=True)

    def process(self, d: date = None, img_folder: Path = None, vid_folder: Path = None) -> Path:
        """
        entry point for timelapse video creation
        :param self: this
        :param date: the date of the video
        :param img_folder: source image folder
        :param vid_folder: destination video folder
        :return: video file path
        """
        if not self._timelapse_config.enable:
            self.logger.warn("timelapse not enabled")
            return None

        start = datetime.now()

        if d is None:
            d = date.today() - timedelta(days=1)

        if img_folder is None:
            img_folder = self._camera_config.folder

        if vid_folder is None:
            vid_folder = self._base_dir

        stamp = d.strftime("%Y-%m-%d")

        images: List[Path] = sorted(img_folder.glob(f"{stamp}*{self._camera_config.extension}"))

        if not images:
            self.logger.warning("No images for %s found in: %s", stamp, img_folder)
            return None

        img = cv2.imread(images[0].resolve())
        height, width, _ = img.shape
        size = (width, height)

        vid_file = (vid_folder / f"{stamp}{self._timelapse_config.extension}").resolve()

        video = cv2.VideoWriter(
            vid_file, cv2.VideoWriter.fourcc(*self._timelapse_config.codec), self._timelapse_config.frames_per_second, size
        )

        try:
            for image in images:
                i = cv2.imread(image.resolve())
                video.write(i)

        finally:
            video.release()
            cv2.destroyAllWindows()

        self.logger.info("time lapse for %s complete  duration %s", stamp, Converter.duration_seconds(start))

        return vid_file
