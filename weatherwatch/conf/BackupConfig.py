from pathlib import Path

from util.Logger import logger

__all__ = ["BackupConfig"]


@logger
class BackupConfig:
    FILE_KEY = "file"
    DB_KEY = "db"
    ENABLE_KEY = "enable"
    FOLDER_KEY = "folder"
    PURGE_KEY = "purge"
    IMG_OLD_KEY = "img_old"
    VID_OLD_KEY = "vid_old"
    WEEKLY_OLD = "weekly_old"

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
    def folder(self) -> Path:
        """
        folder property getter
        :param self: this
        :return: the folder
        """
        return Path(self.__dict__[BackupConfig.FOLDER_KEY])

    @property
    def file_enable(self) -> bool:
        """
        file_enable property getter
        :param self: this
        :return: the file_enable
        """
        return self.__dict__[BackupConfig.FILE_KEY][BackupConfig.ENABLE_KEY]

    @property
    def db_enable(self) -> bool:
        """
        db_enable property getter
        :param self: this
        :return: the db_enable
        """
        return self.__dict__[BackupConfig.DB_KEY][BackupConfig.ENABLE_KEY]

    @property
    def purge_enable(self) -> bool:
        """
        purge_enable property getter
        :param self: this
        :return: the purge_enable
        """
        return self.__dict__[BackupConfig.PURGE_KEY][BackupConfig.ENABLE_KEY]

    @property
    def img_old(self) -> int:
        """
        img_old property getter
        :param self: this
        :return: the img_old
        """
        return self.__dict__[BackupConfig.PURGE_KEY][BackupConfig.IMG_OLD_KEY]

    @property
    def vid_old(self) -> int:
        """
        vid_old property getter
        :param self: this
        :return: the vid_old
        """
        return self.__dict__[BackupConfig.PURGE_KEY][BackupConfig.VID_OLD_KEY]

    @property
    def db_weekly_old(self) -> int:
        """
        db_weekly_old property getter
        :param self: this
        :return: the db_weekly_old
        """
        return self.__dict__[BackupConfig.DB_KEY][BackupConfig.WEEKLY_OLD]
