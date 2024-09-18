import yaml
import logging
import logging.config

from typing import List

from src.conf.DatabaseConfig import DatabaseConfig
from src.conf.SensorConfig import SensorConfig

class AppConfig(object):
    CONFIG_FILE = 'config/weatherwatch.yml'
    LOG_CONFIG_FILE = 'config/logging.yml'
    SDR_KEY = 'sdr'
    READER_KEY = 'reader'
    SENSORS_KEY = 'sensors'
    DATABASE_KEY = 'database'
   
    """
    app config data 
    """
    
    # override for singleton
    # https://www.geeksforgeeks.org/singleton-pattern-in-python-a-complete-guide/
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AppConfig, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        """
        ctor
        :param self: this
        """
        
        # https://coding-stream-of-consciousness.com/2018/11/26/logging-in-python-3-like-java-log4j-logback/
        # https://docs.python.org/3/library/logging.html#logrecord-attributes
        with open(AppConfig.LOG_CONFIG_FILE, 'rt') as f:
            lc = yaml.safe_load(f.read())
            logging.config.dictConfig(lc)        
    
        logging.info("loaded logging config " + AppConfig.LOG_CONFIG_FILE)
       
        with open(AppConfig.CONFIG_FILE) as f:
            self._conf = yaml.safe_load(f)

        logging.info("loaded application config " + AppConfig.CONFIG_FILE)

        self._sensors = []
        
        for s in self._conf[AppConfig.SDR_KEY][AppConfig.SENSORS_KEY]:
             self._sensors.append(SensorConfig(s))
           
        self._database =  DatabaseConfig(self._conf[AppConfig.DATABASE_KEY])  
    
    #override
    def __str__(self):
        return str(self.__dict__)

    @property
    def conf(self) -> dict:
        """
        conf property getter
        :param self: this
        :return: the conf
        """
        return self._conf
    
    @property
    def sensors(self) -> List[SensorConfig]:
        """
        sensors property getter
        :param self: this
        :return: the sensors
        """
        return self._sensors
    
    @property
    def database(self) -> DatabaseConfig:
        """
        database property getter
        :param self: this
        :return: the database
        """
        return self._database