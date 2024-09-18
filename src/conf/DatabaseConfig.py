import os

class DatabaseConfig(object):
    # TODO defaults?
    NAME_KEY = 'name'
    DIALECT_KEY = 'dialect'
    DRIVER_KEY = 'driver'
    HOST_KEY = 'host'
    PORT_KEY = 'port'

    # TODO envars placed in /etc/environment and not in user space
    USERNAME_ENVAR = 'WW_DB_USERNAME'
    PASSWORD_ENVAR = 'WW_DB_USERNAME'
    
    # https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls
    # https://ankushkunwar7777.medium.com/connect-mysql-to-sqlalchemy-in-python-b94c34568818
    # dialect+driver://username:password@host:port/database
    URL_TEMPLATE = '{dialect}+{driver}://{username}:{password}@{host}:{port}/{database}'

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
        
    #override
    def __str__(self):
        return str(self.__dict__)
    
    @property
    def url(self):
        """
        name property getter
        :param self: this
        :return: the name
        """
        return DatabaseConfig.URL_TEMPLATE.format(
            dialect = self.__dict__[DatabaseConfig.DIALECT_KEY], 
            driver = self.__dict__[DatabaseConfig.DRIVER_KEY], 
            username = os.environ[DatabaseConfig.USERNAME_ENVAR], 
            password = os.environ[DatabaseConfig.PASSWORD_ENVAR], 
            host = self.__dict__[DatabaseConfig.HOST_KEY], 
            port = self.__dict__[DatabaseConfig.PORT_KEY], 
            database = self.__dict__[DatabaseConfig.NAME_KEY])
