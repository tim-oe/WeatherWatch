__all__ = ["SchedulerConfig"]


from util.Logger import logger


@logger
class SchedulerConfig:
    SENSOR_KEY = "sensor"
    CAMERA_KEY = "camera"
    AQI_KEY = "aqi"
    PIMETRICS_KEY = "pimetrics"
    TIMELAPSE_KEY = "timelapse"
    WU_KEY = "weather_undergound"
    INTERVAL_KEY = "interval"
    START_KEY = "start"
    STOP_KEY = "stop"
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
    def cameraStart(self) -> int:
        """
        camera start property getter
        :param self: this
        :return: the camera start
        """
        return self.__dict__[SchedulerConfig.CAMERA_KEY][SchedulerConfig.START_KEY]

    @property
    def cameraStop(self) -> int:
        """
        camera stop property getter
        :param self: this
        :return: the camera stop
        """
        return self.__dict__[SchedulerConfig.CAMERA_KEY][SchedulerConfig.STOP_KEY]

    @property
    def timelapseHour(self) -> int:
        """
        timelapse Hour property getter
        :param self: this
        :return: the timelapse Hour
        """
        return self.__dict__[SchedulerConfig.TIMELAPSE_KEY][SchedulerConfig.HOUR_KEY]
