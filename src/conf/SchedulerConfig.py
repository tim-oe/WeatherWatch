__all__ = ["SchedulerConfig"]


class SchedulerConfig:
    SENSOR_KEY = "sensor"
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
    def sensorInterval(self) -> int:
        """
        id property getter
        :param self: this
        :return: the id
        """
        return self.__dict__[SchedulerConfig.SENSOR_KEY][SchedulerConfig.INTERVAL_KEY]
