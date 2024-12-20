from pathlib import Path

from util.Logger import logger

__all__ = ["TimelapseConfig"]


@logger
class TimelapseConfig:
    """
    Timelapse config data
    """

    ENABLE_KEY = "enable"
    FOLDER_KEY = "folder"
    EXTENSION_KEY = "extension"
    FPS_KEY = "fps"
    CODEC_KEY = "codec"

    def __init__(self, config: dict):
        """
        ctor
        :param self: this
        """

        for key in config:
            self.__dict__[key] = config[key]

    @property
    def enable(self) -> bool:
        """
        enable property getter
        :param self: this
        :return: the enable
        """
        return self.__dict__[TimelapseConfig.ENABLE_KEY]

    @property
    def folder(self) -> Path:
        """
        folder property getter
        :param self: this
        :return: the folder
        """
        return Path(self.__dict__[TimelapseConfig.FOLDER_KEY])

    @property
    def extension(self) -> str:
        """
        extension property getter
        :param self: this
        :return: the extension
        """
        return self.__dict__[TimelapseConfig.EXTENSION_KEY]

    @property
    def frames_per_second(self) -> int:
        """
        framesPerSecond property getter
        :param self: this
        :return: the framesPerSecond
        """
        return self.__dict__[TimelapseConfig.FPS_KEY]

    @property
    def codec(self) -> int:
        """
        codec property getter
        :param self: this
        :return: the codec
        """
        return self.__dict__[TimelapseConfig.CODEC_KEY]
