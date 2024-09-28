import logging
import logging.config
import os
from typing import List

from pyaml_env import parse_config

from conf.DatabaseConfig import DatabaseConfig
from conf.SchedulerConfig import SchedulerConfig
from conf.SensorConfig import SensorConfig

__all__ = ["AppConfig"]


class AppConfig(object):
    CONFIG_FILE = "config/weatherwatch.yml"
    LOG_CONFIG_FILE = "config/logging.yml"

    ENVAR_NO_CONSOLE = "WW_NO_CONSOLE"

    SDR_KEY = "sdr"
    READER_KEY = "reader"
    SENSORS_KEY = "sensors"
    DATABASE_KEY = "database"
    SCHEDULER_KEY = "scheduler"

    """
    app config data
    envar ebedded yaml config
    https://pyyaml.org/wiki/PyYAMLDocumentation
    https://pypi.org/project/pyaml-env/
    """

    # override for singleton
    # https://www.geeksforgeeks.org/singleton-pattern-in-python-a-complete-guide/
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(AppConfig, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self.logging()

        self._conf = parse_config(AppConfig.CONFIG_FILE)

        logging.info("loaded application config " + AppConfig.CONFIG_FILE)

        self._sensors = []

        for s in self._conf[AppConfig.SDR_KEY][AppConfig.SENSORS_KEY]:
            self._sensors.append(SensorConfig(s))
        logging.info("loaded sensors config")

        self._database = DatabaseConfig(self._conf[AppConfig.DATABASE_KEY])
        logging.info("loaded database config")

        self._scheduler = SchedulerConfig(self._conf[AppConfig.SCHEDULER_KEY])
        logging.info("loaded scheduler config")

    def logging(self):
        # https://coding-stream-of-consciousness.com/2018/11/26/logging-in-python-3-like-java-log4j-logback/
        # https://docs.python.org/3/library/logging.html#logrecord-attributes
        # https://gist.github.com/kingspp/9451566a5555fb022215ca2b7b802f19
        lc: dict = parse_config(AppConfig.LOG_CONFIG_FILE)

        logging.config.dictConfig(lc)

        if os.getenv(AppConfig.ENVAR_NO_CONSOLE, "0") == "1":
            c: logging.Handler = None
            for h in logging.root.handlers:
                h: logging.Handler
                if h.name == "console":
                    c = h
            logging.root.handlers.remove(c)

        logging.info("loaded logging config " + AppConfig.LOG_CONFIG_FILE)

    # override
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

    @property
    def scheduler(self) -> SchedulerConfig:
        """
        scheduler property getter
        :param self: this
        :return: the scheduler
        """
        return self._scheduler
