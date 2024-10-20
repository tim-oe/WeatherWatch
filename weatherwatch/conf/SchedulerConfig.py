__all__ = ["SchedulerConfig"]


class SchedulerConfig:
    SENSOR_KEY = "sensor"
    CAMERA_KEY = "camera"
    AQI_KEY = "aqi"
    PIMETRICS_KEY = "pimetrics"
    INTERVAL_KEY = "interval"

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

    # override
    def __str__(self):
        return str(self.__dict__)

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
        camera inerval property getter
        :param self: this
        :return: the camera inerval
        """
        return self.__dict__[SchedulerConfig.CAMERA_KEY][SchedulerConfig.INTERVAL_KEY]
