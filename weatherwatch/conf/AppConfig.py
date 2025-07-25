import logging.config
import os
from typing import List

from conf.AQIConfig import AQIConfig
from conf.BackupConfig import BackupConfig
from conf.CameraConfig import CameraConfig
from conf.DashConfig import DashConfig
from conf.DatabaseConfig import DatabaseConfig
from conf.EmailConfig import EmailConfig
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
    """
    app config data
    envar ebedded yaml config
    https://pyyaml.org/wiki/PyYAMLDocumentation
    https://pypi.org/project/pyaml-env/
    """

    CONFIG_FILE = "config/weatherwatch.yml"
    LOG_CONFIG_FILE = "config/logging.yml"

    ENVAR_NO_CONSOLE = "WW_NO_CONSOLE"

    SDR_KEY = "sdr"
    GPS_KEY = "gps"
    AQI_KEY = "aqi"
    READER_KEY = "reader"
    SENSORS_KEY = "sensors"
    DATABASE_KEY = "database"
    EMAIL_KEY = "email"
    CAMERA_KEY = "camera"
    BACKUP_KEY = "backup"
    SCHEDULER_KEY = "scheduler"
    DASHBOARD_KEY = "dashboard"
    TIMELAPSE_KEY = "timelapse"
    WU_KEY = "weather_undergound"

    CONF_INIT_MSG = "loaded %s config"

    def __init__(self):
        """
        ctor
        :param self: this
        """

        self.init_logging()

        self._conf = parse_config(AppConfig.CONFIG_FILE)

        self.logger.info("loaded application config file %s", AppConfig.CONFIG_FILE)

        self._sensors = {}

        for s in self._conf[AppConfig.SDR_KEY][AppConfig.SENSORS_KEY]:
            ss: SensorConfig = SensorConfig(s)
            self._sensors[ss.name] = ss

        self.logger.info(AppConfig.CONF_INIT_MSG, AppConfig.SENSORS_KEY)

        self._aqi = AQIConfig(self._conf[AppConfig.AQI_KEY])
        self.logger.info(AppConfig.CONF_INIT_MSG, AppConfig.AQI_KEY)

        self._camera = CameraConfig(self._conf[AppConfig.CAMERA_KEY])
        self.logger.info(AppConfig.CONF_INIT_MSG, AppConfig.CAMERA_KEY)

        self._dashboard = DashConfig(self._conf[AppConfig.DASHBOARD_KEY])
        self.logger.info(AppConfig.CONF_INIT_MSG, AppConfig.DASHBOARD_KEY)

        self._database = DatabaseConfig(self._conf[AppConfig.DATABASE_KEY])
        self.logger.info(AppConfig.CONF_INIT_MSG, AppConfig.DATABASE_KEY)

        self._email = EmailConfig(self._conf[AppConfig.EMAIL_KEY])
        self.logger.info(AppConfig.CONF_INIT_MSG, AppConfig.EMAIL_KEY)

        self._file_backup = BackupConfig(self._conf[AppConfig.BACKUP_KEY])
        self.logger.info(AppConfig.CONF_INIT_MSG, AppConfig.BACKUP_KEY)

        self._gps = GPSConfig(self._conf[AppConfig.GPS_KEY])
        self.logger.info(AppConfig.CONF_INIT_MSG, AppConfig.GPS_KEY)

        self._scheduler = SchedulerConfig(self._conf[AppConfig.SCHEDULER_KEY])
        self.logger.info(AppConfig.CONF_INIT_MSG, AppConfig.SCHEDULER_KEY)

        self._timelapse = TimelapseConfig(self._conf[AppConfig.TIMELAPSE_KEY])
        self.logger.info(AppConfig.CONF_INIT_MSG, AppConfig.TIMELAPSE_KEY)

        self._wu = WUConfig(self._conf[AppConfig.WU_KEY])
        self.logger.info(AppConfig.CONF_INIT_MSG, AppConfig.WU_KEY)

    def init_logging(self):
        """
        initialize logging
        https://coding-stream-of-consciousness.com/2018/11/26/logging-in-python-3-like-java-log4j-logback/
        https://docs.python.org/3/library/self.logger.html#logrecord-attributes
        https://gist.github.com/kingspp/9451566a5555fb022215ca2b7b802f19
        :param self: this
        """

        lc: dict = parse_config(AppConfig.LOG_CONFIG_FILE)

        logging.config.dictConfig(lc)  # NOSONAR (python:S4792)

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

    def get_sensor(self, name: str) -> SensorConfig:
        """
        get sensor config based on name
        :param self: this
        :param name: the name of the sensor config
        :return: the sensor config
        """
        return self._sensors[name]

    @property
    def aqi(self) -> AQIConfig:
        """
        aqi property getter
        :param self: this
        :return: the aqi config
        """
        return self._aqi

    @property
    def camera(self) -> CameraConfig:
        """
        camera property getter
        :param self: this
        :return: the camera
        """
        return self._camera

    @property
    def dashboard(self) -> DashConfig:
        """
        dashboard property getter
        :param self: this
        :return: the dashboard
        """
        return self._dashboard

    @property
    def database(self) -> DatabaseConfig:
        """
        database property getter
        :param self: this
        :return: the database
        """
        return self._database

    @property
    def email(self) -> EmailConfig:
        """
        email property getter
        :param self: this
        :return: the email
        """
        return self._email

    @property
    def backup(self) -> BackupConfig:
        """
        file_backup property getter
        :param self: this
        :return: the file_backup
        """
        return self._file_backup

    @property
    def gps(self) -> GPSConfig:
        """
        gps property getter
        :param self: this
        :return: the gps
        """
        return self._gps

    @property
    def scheduler(self) -> SchedulerConfig:
        """
        scheduler property getter
        :param self: this
        :return: the scheduler
        """
        return self._scheduler

    @property
    def timelapse(self) -> TimelapseConfig:
        """
        timelapse property getter
        :param self: this
        :return: the timelapse
        """
        return self._timelapse

    @property
    def wu(self) -> WUConfig:
        """
        wu property getter
        :param self: this
        :return: the wu
        """
        return self._wu
