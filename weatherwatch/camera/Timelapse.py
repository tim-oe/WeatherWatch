import logging
from datetime import date, timedelta
from pathlib import Path
from typing import List

import cv2
from conf.AppConfig import AppConfig
from conf.CameraConfig import CameraConfig
from conf.TimelapseConfig import TimelapseConfig
from py_singleton import singleton


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

        self._cameraConfig: CameraConfig = AppConfig().camera
        self._timelapseConfig: TimelapseConfig = AppConfig().timelapse

        self._baseDir: Path = self._timelapseConfig.folder

        self._baseDir.mkdir(parents=True, exist_ok=True)

    def process(self, d: date = None, imgFolder: Path = None, vidFolder: Path = None) -> Path:
        if d is None:
            d = date.today() - timedelta(days=1)

        if imgFolder is None:
            imgFolder = self._cameraConfig.folder

        if vidFolder is None:
            vidFolder = self._baseDir

        stamp = d.strftime("%Y-%m-%d")

        images: List[Path] = sorted(imgFolder.glob(f"{stamp}*{self._cameraConfig.extension}"))

        if not images:
            logging.warning("No images for %s found in: %s", stamp, imgFolder)
            return

        img = cv2.imread(images[0].resolve())
        height, width, _ = img.shape
        size = (width, height)

        vidFile = (vidFolder / f"{stamp}{self._timelapseConfig.extension}").resolve()

        video = cv2.VideoWriter(
            vidFile, cv2.VideoWriter.fourcc(*self._timelapseConfig.codec), self._timelapseConfig.framesPerSecond, size
        )

        try:
            for image in images:
                i = cv2.imread(image.resolve())
                video.write(i)

        finally:
            video.release()
            cv2.destroyAllWindows()

        return vidFile
