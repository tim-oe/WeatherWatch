__all__ = ["SchedulerConfig"]


from util.Logger import logger


@logger
class SchedulerConfig:
    AQI_KEY = "aqi"
    CAMERA_KEY = "camera"
    FILE_BACKUP_KEY = "file_backup"
    PIMETRICS_KEY = "pimetrics"
    SENSOR_KEY = "sensor"
    TIMELAPSE_KEY = "timelapse"
    WU_KEY = "weather_undergound"
    INTERVAL_KEY = "interval"
    HOUR_KEY = "hour"

    """
    scheduler config data
    """

    def __init__(self, config: dict):
        """
        ctor
        :param self: this
        """

        for key in config:
            self.__dict__[key] = config[key]

    @property
    def aqiInterval(self) -> int:
        """
        aqi inerval property getter
        :param self: this
        :return: the aqi inerval
        """
        return self.__dict__[SchedulerConfig.AQI_KEY][SchedulerConfig.INTERVAL_KEY]

    @property
    def sensorInterval(self) -> int:
        """
        sensor inerval property getter
        :param self: this
        :return: the sensor inerval
        """
        return self.__dict__[SchedulerConfig.SENSOR_KEY][SchedulerConfig.INTERVAL_KEY]

    @property
    def wuInterval(self) -> int:
        """
        weather underground inerval property getter
        :param self: this
        :return: the weather underground inerval
        """
        return self.__dict__[SchedulerConfig.WU_KEY][SchedulerConfig.INTERVAL_KEY]

    @property
    def piMetricsInterval(self) -> int:
        """
        pimetrics inerval property getter
        :param self: this
        :return: the pimetrics inerval
        """
        return self.__dict__[SchedulerConfig.PIMETRICS_KEY][SchedulerConfig.INTERVAL_KEY]

    @property
    def cameraInterval(self) -> int:
        """
        camera interval property getter
        :param self: this
        :return: the camera interval
        """
        return self.__dict__[SchedulerConfig.CAMERA_KEY][SchedulerConfig.INTERVAL_KEY]

    @property
    def timelapseHour(self) -> int:
        """
        timelapse Hour property getter
        :param self: this
        :return: the timelapse Hour
        """
        return self.__dict__[SchedulerConfig.TIMELAPSE_KEY][SchedulerConfig.HOUR_KEY]

    @property
    def file_back_hour(self) -> int:
        """
        file_backup Hour property getter
        :param self: this
        :return: the file_backup Hour
        """
        return self.__dict__[SchedulerConfig.FILE_BACKUP_KEY][SchedulerConfig.HOUR_KEY]
