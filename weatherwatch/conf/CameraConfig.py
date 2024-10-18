from pathlib import Path

__all__ = ["CameraConfig"]


class CameraConfig:
    ENABLE_KEY = "enable"
    FOLDER_KEY = "folder"
    EXTENSION_KEY = "extension"
    TUNING_KEY = "tuning"
    TUNING_FILE_KEY = "file"

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
