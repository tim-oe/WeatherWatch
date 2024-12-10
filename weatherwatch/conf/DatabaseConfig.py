__all__ = ["DatabaseConfig"]

import os

from sqlalchemy import URL
from util.Logger import logger


@logger
class DatabaseConfig:
    NAME_KEY = "name"
    DIALECT_KEY = "dialect"
    DRIVER_KEY = "driver"
    HOST_KEY = "host"
    PORT_KEY = "port"
    USERNAME_KEY = "username"
    PASSWORD_KEY = "password"
    PRODUCTION_KEY = "production"
    POOL_KEY = "pool"
    SIZE_KEY = "size"
    OVERFLOW_KEY = "overflow"
    BACKUP_KEY = "backup"
    ENABLE_KEY = "enable"
    FOLDER_KEY = "folder"

    # TODO envars placed in /etc/environment and not in user space
    USERNAME_ENVAR = "WW_DB_USERNAME"
    PASSWORD_ENVAR = "WW_DB_PASSWORD"

    # https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls
    # https://ankushkunwar7777.medium.com/connect-mysql-to-sqlalchemy-in-python-b94c34568818
    # https://docs.sqlalchemy.org/en/20/dialects/mysql.html#module-sqlalchemy.dialects.mysql.mariadbconnector

    """
    database config data
    """

    def __init__(self, config: dict):
        """
        ctor
        :param self: this
        """
        for key in config:
            self.__dict__[key] = config[key]

        if DatabaseConfig.USERNAME_ENVAR not in os.environ or DatabaseConfig.PASSWORD_ENVAR not in os.environ:
            raise Exception("missing env var " + DatabaseConfig.USERNAME_ENVAR + "," + DatabaseConfig.PASSWORD_ENVAR)

    @property
    def production(self) -> bool:
        """
        production property getter
        this defaults to true and is a weak
        mechanism to prevent bad stuff running on prod
        :param self: this
        :return: the production
        """
        return self.__dict__[DatabaseConfig.PRODUCTION_KEY]

    @property
    def url(self) -> URL:
        """
        name property getter
        :param self: this
        :return: the name
        """
        return URL.create(
            self.__dict__[DatabaseConfig.DIALECT_KEY] + "+" + self.__dict__[DatabaseConfig.DRIVER_KEY],
            username=self.__dict__[DatabaseConfig.USERNAME_KEY],
            password=self.__dict__[DatabaseConfig.PASSWORD_KEY],
            host=self.__dict__[DatabaseConfig.HOST_KEY],
            port=self.__dict__[DatabaseConfig.PORT_KEY],
            database=self.__dict__[DatabaseConfig.NAME_KEY],
        )

    @property
    def pool_size(self) -> int:
        """
        pool_size property getter
        :param self: this
        :return: the pool_size
        """
        return self.__dict__[DatabaseConfig.POOL_KEY][DatabaseConfig.SIZE_KEY]

    @property
    def pool_overflow(self) -> int:
        """
        pool_size property getter
        :param self: this
        :return: the pool_size
        """
        return self.__dict__[DatabaseConfig.POOL_KEY][DatabaseConfig.OVERFLOW_KEY]

    @property
    def backupEnable(self) -> bool:
        """
        backupEnable property getter
        :param self: this
        :return: the backupEnable
        """
        return self.__dict__[DatabaseConfig.BACKUP_KEY][DatabaseConfig.ENABLE_KEY]

    @property
    def backupFolder(self) -> bool:
        """
        backupFolder property getter
        :param self: this
        :return: the backupFolder
        """
        return self.__dict__[DatabaseConfig.BACKUP_KEY][DatabaseConfig.FOLDER_KEY]
