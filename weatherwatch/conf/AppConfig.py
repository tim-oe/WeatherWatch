import logging.config
import os
from typing import List

from conf.AQIConfig import AQIConfig
from conf.CameraConfig import CameraConfig
from conf.DashConfig import DashConfig
from conf.DatabaseConfig import DatabaseConfig
from conf.GPSConfig import GPSConfig
from conf.SchedulerConfig import SchedulerConfig
from conf.SensorConfig import SensorConfig
from conf.TimelapseConfig import TimelapseConfig
from conf.WUConfig import WUConfig
from py_singleton import singleton
from pyaml_env import parse_config
from util.Logger import logger

__all__ = ["AppConfig"]


@logger
@singleton
class AppConfig:

    CONFIG_FILE = "config/weatherwatch.yml"
    LOG_CONFIG_FILE = "config/logging.yml"

    ENVAR_NO_CONSOLE = "WW_NO_CONSOLE"

    SDR_KEY = "sdr"
    GPS_KEY = "gps"
    AQI_KEY = "aqi"
    READER_KEY = "reader"
    SENSORS_KEY = "sensors"
    DATABASE_KEY = "database"
    CAMERA_KEY = "camera"
    SCHEDULER_KEY = "scheduler"
    DASHBOARD_KEY = "dashboard"
    TIMELAPSE_KEY = "timelapse"
    WU_KEY = "weather_undergound"

    """
    app config data
    envar ebedded yaml config
    https://pyyaml.org/wiki/PyYAMLDocumentation
    https://pypi.org/project/pyaml-env/
    """

    def __init__(self):
        """
        ctor
        :param self: this
        """

        self.initLogging()

        self._conf = parse_config(AppConfig.CONFIG_FILE)

        self.logger.info("loaded application config file %s", AppConfig.CONFIG_FILE)

        self._sensors = {}

        for s in self._conf[AppConfig.SDR_KEY][AppConfig.SENSORS_KEY]:
            ss: SensorConfig = SensorConfig(s)
            self._sensors[ss.name] = ss

        self.logger.info("loaded %s config", AppConfig.SENSORS_KEY)

        self._camera = CameraConfig(self._conf[AppConfig.CAMERA_KEY])
        self.logger.info("loaded %s config", AppConfig.CAMERA_KEY)

        self._aqi = AQIConfig(self._conf[AppConfig.AQI_KEY])
        self.logger.info("loaded %s config", AppConfig.AQI_KEY)

        self._gps = GPSConfig(self._conf[AppConfig.GPS_KEY])
        self.logger.info("loaded %s config", AppConfig.GPS_KEY)

        self._database = DatabaseConfig(self._conf[AppConfig.DATABASE_KEY])
        self.logger.info("loaded %s config", AppConfig.DATABASE_KEY)

        self._scheduler = SchedulerConfig(self._conf[AppConfig.SCHEDULER_KEY])
        self.logger.info("loaded %s config", AppConfig.SCHEDULER_KEY)

        self._dashboard = DashConfig(self._conf[AppConfig.DASHBOARD_KEY])
        self.logger.info("loaded %s config", AppConfig.DASHBOARD_KEY)

        self._timelapse = TimelapseConfig(self._conf[AppConfig.TIMELAPSE_KEY])
        self.logger.info("loaded %s config", AppConfig.TIMELAPSE_KEY)

        self._wu = WUConfig(self._conf[AppConfig.WU_KEY])
        self.logger.info("loaded %s config", AppConfig.WU_KEY)

    def initLogging(self):
        # https://coding-stream-of-consciousness.com/2018/11/26/logging-in-python-3-like-java-log4j-logback/
        # https://docs.python.org/3/library/self.logger.html#logrecord-attributes
        # https://gist.github.com/kingspp/9451566a5555fb022215ca2b7b802f19
        lc: dict = parse_config(AppConfig.LOG_CONFIG_FILE)

        logging.config.dictConfig(lc)

        # https://stackoverflow.com/questions/7484454/removing-handlers-from-pythons-logging-loggers
        if os.getenv(AppConfig.ENVAR_NO_CONSOLE, "0") == "1":
            logging.root.handlers = [h for h in logging.root.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]

        logging.info("loaded logging config file %s", AppConfig.LOG_CONFIG_FILE)

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
        return list(self._sensors.values())

    def getSensor(self, name: str) -> SensorConfig:
        return self._sensors[name]

    @property
    def camera(self) -> CameraConfig:
        """
        camera property getter
        :param self: this
        :return: the camera
        """
        return self._camera

    @property
    def timelapse(self) -> TimelapseConfig:
        """
        timelapse property getter
        :param self: this
        :return: the timelapse
        """
        return self._timelapse

    @property
    def aqi(self) -> AQIConfig:
        """
        aqi property getter
        :param self: this
        :return: the aqi
        """
        return self._aqi

    @property
    def gps(self) -> AQIConfig:
        """
        gps property getter
        :param self: this
        :return: the gps
        """
        return self._gps

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

    @property
    def dashboard(self) -> DashConfig:
        """
        dashboard property getter
        :param self: this
        :return: the dashboard
        """
        return self._dashboard

    @property
    def wu(self) -> WUConfig:
        """
        wu property getter
        :param self: this
        :return: the wu
        """
        return self._wu
