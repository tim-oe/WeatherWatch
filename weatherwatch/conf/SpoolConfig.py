from pathlib import Path

from util.Logger import logger

__all__ = ["SpoolConfig"]


@logger
class SpoolConfig:
    """
    offline spool config data
    """

    ENABLE_KEY = "enable"
    FOLDER_KEY = "folder"
    MIN_FREE_PCT_KEY = "min_free_pct"
    WARN_AGE_HOURS_KEY = "warn_age_hours"

    def __init__(self, config: dict):
        """
        ctor
        :param self: this
        :param config: the spool config mapping
        """
        for key in config:
            self.__dict__[key] = config[key]

    @property
    def enable(self) -> bool:
        """
        enable property getter
        :param self: this
        :return: the enable flag
        """
        return self.__dict__[SpoolConfig.ENABLE_KEY]

    @property
    def folder(self) -> Path:
        """
        folder property getter
        :param self: this
        :return: the spool folder
        """
        return Path(self.__dict__[SpoolConfig.FOLDER_KEY])

    @property
    def min_free_pct(self) -> int:
        """
        min_free_pct property getter
        :param self: this
        :return: the free-space floor percent
        """
        return self.__dict__[SpoolConfig.MIN_FREE_PCT_KEY]

    @property
    def warn_age_hours(self) -> int:
        """
        warn_age_hours property getter
        :param self: this
        :return: the age warning threshold in hours
        """
        return self.__dict__[SpoolConfig.WARN_AGE_HOURS_KEY]
