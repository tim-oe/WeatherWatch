import yaml
import logging
import logging.config

from typing import List

from src.conf.SensorConfig import SensorConfig

class AppConfig(object):
    CONFIG_FILE = 'config/weatherwatch.yml'
    LOG_CONFIG_FILE = 'config/logging.yml'
    SENSORS_KEY = 'sensors'
    
    """
    sensor config data 
    """
    def __init__(self):
        """
        ctor
        :param self: this
        """
        with open(AppConfig.LOG_CONFIG_FILE, 'rt') as f:
            lc = yaml.safe_load(f.read())
            logging.config.dictConfig(lc)        
       
        logging.info("loaded logging config " + AppConfig.LOG_CONFIG_FILE)
       
        with open(AppConfig.CONFIG_FILE) as f:
            self._conf = yaml.safe_load(f)

        logging.info("loaded application config " + AppConfig.CONFIG_FILE)

        self._sensors = []
        
        for s in self._conf[AppConfig.SENSORS_KEY]:
             self._sensors.append(SensorConfig(s))
           
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
        return self.self._sensors

