from pathlib import Path

from util.Logger import logger

__all__ = ["CameraConfig"]


@logger
class CameraConfig:
    """
    camera config data
    """

    ENABLE_KEY = "enable"
    FOLDER_KEY = "folder"
    LUX_LIMIT_KEY = "lux_limit"
    EXPOSURE_TIME_KEY = "exposure_time"
    ANALOGUE_GAIN_KEY = "analogue_gain"
    EXTENSION_KEY = "extension"
    TUNING_KEY = "tuning"
    TUNING_FILE_KEY = "file"
    LENS_KEY = "lens"
    MAKE_KEY = "make"
    MODEL_KEY = "model"

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
        return self.__dict__[CameraConfig.ENABLE_KEY]

    @property
    def lux_limit(self) -> int:
        """
        luxLimit property getter
        :param self: this
        :return: the luxLimit
        """
        return self.__dict__[CameraConfig.LUX_LIMIT_KEY]

    @property
    def exposure_time(self) -> int:
        """
        exposureTime property getter
        :param self: this
        :return: the exposureTime
        """
        return self.__dict__[CameraConfig.EXPOSURE_TIME_KEY]

    @property
    def analogue_gain(self) -> float:
        """
        analogueGain property getter
        :param self: this
        :return: the analogueGain
        """
        return self.__dict__[CameraConfig.ANALOGUE_GAIN_KEY]

    @property
    def folder(self) -> Path:
        """
        folder property getter
        :param self: this
        :return: the folder
        """
        return Path(self.__dict__[CameraConfig.FOLDER_KEY])

    @property
    def extension(self) -> str:
        """
        extension property getter
        :param self: this
        :return: the extension
        """
        return self.__dict__[CameraConfig.EXTENSION_KEY]

    @property
    def current_file(self) -> Path:
        """
        current_file property getter
        :param self: this
        :return: the current_file
        """
        return self.folder / f"current{self.extension}"

    @property
    def tuning_enable(self) -> bool:
        """
        tuningEnable property getter
        :param self: this
        :return: the tuningEnable
        """
        return self.__dict__[CameraConfig.TUNING_KEY][CameraConfig.ENABLE_KEY]

    @property
    def tuning_file(self) -> str:
        """
        tuningFile property getter
        :param self: this
        :return: the tuningFile
        """
        return self.__dict__[CameraConfig.TUNING_KEY][CameraConfig.TUNING_FILE_KEY]

    @property
    def lens_make(self) -> str:
        """
        lensMake property getter
        :param self: this
        :return: the lensMake
        """
        return self.__dict__[CameraConfig.LENS_KEY][CameraConfig.MAKE_KEY]

    @property
    def lens_model(self) -> str:
        """
        lensModel property getter
        :param self: this
        :return: the lensModel
        """
        return self.__dict__[CameraConfig.LENS_KEY][CameraConfig.MODEL_KEY]
