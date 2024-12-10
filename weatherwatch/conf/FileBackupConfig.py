from pathlib import Path

from util.Logger import logger

__all__ = ["FileBackupConfig"]


@logger
class FileBackupConfig:
    ENABLE_KEY = "enable"
    FOLDER_KEY = "folder"
    PURGE_KEY = "purge"
    IMG_OLD_KEY = "img_old"
    VID_OLD_KEY = "vid_old"

    """
    file backup config data
    """

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
        return self.__dict__[FileBackupConfig.ENABLE_KEY]

    @property
    def folder(self) -> Path:
        """
        folder property getter
        :param self: this
        :return: the folder
        """
        return Path(self.__dict__[FileBackupConfig.FOLDER_KEY])

    @property
    def purge_enable(self) -> bool:
        """
        purge_enable property getter
        :param self: this
        :return: the purge_enable
        """
        return self.__dict__[FileBackupConfig.PURGE_KEY][FileBackupConfig.ENABLE_KEY]

    @property
    def img_old(self) -> int:
        """
        img_old property getter
        :param self: this
        :return: the img_old
        """
        return self.__dict__[FileBackupConfig.PURGE_KEY][FileBackupConfig.IMG_OLD_KEY]

    @property
    def vid_old(self) -> int:
        """
        vid_old property getter
        :param self: this
        :return: the vid_old
        """
        return self.__dict__[FileBackupConfig.PURGE_KEY][FileBackupConfig.VID_OLD_KEY]
