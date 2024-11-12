from pathlib import Path

__all__ = ["CameraConfig"]


class CameraConfig:
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

    """
    camera config data
    """

    def __init__(self, config: dict):
        """
        ctor
        :param self: this
        """

        for key in config:
            self.__dict__[key] = config[key]

    # override
    def __str__(self):
        return str(self.__dict__)

    @property
    def enable(self) -> bool:
        """
        enable property getter
        :param self: this
        :return: the enable
        """
        return self.__dict__[CameraConfig.ENABLE_KEY]

    @property
    def luxLimit(self) -> int:
        """
        luxLimit property getter
        :param self: this
        :return: the luxLimit
        """
        return self.__dict__[CameraConfig.LUX_LIMIT_KEY]

    @property
    def exposureTime(self) -> int:
        """
        exposureTime property getter
        :param self: this
        :return: the exposureTime
        """
        return self.__dict__[CameraConfig.EXPOSURE_TIME_KEY]

    @property
    def analogueGain(self) -> float:
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
    def currentFile(self) -> Path:
        """
        extension property getter
        :param self: this
        :return: the extension
        """
        return self.folder / f"current{self.extension}"

    @property
    def tuningEnable(self) -> bool:
        """
        tuningEnable property getter
        :param self: this
        :return: the tuningEnable
        """
        return self.__dict__[CameraConfig.TUNING_KEY][CameraConfig.ENABLE_KEY]

    @property
    def tuningFile(self) -> str:
        """
        tuningFile property getter
        :param self: this
        :return: the tuningFile
        """
        return self.__dict__[CameraConfig.TUNING_KEY][CameraConfig.TUNING_FILE_KEY]

    @property
    def lensMake(self) -> str:
        """
        lensMake property getter
        :param self: this
        :return: the lensMake
        """
        return self.__dict__[CameraConfig.LENS_KEY][CameraConfig.MAKE_KEY]

    @property
    def lensModel(self) -> str:
        """
        lensModel property getter
        :param self: this
        :return: the lensModel
        """
        return self.__dict__[CameraConfig.LENS_KEY][CameraConfig.MODEL_KEY]
