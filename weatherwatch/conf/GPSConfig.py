__all__ = ["GPSConfig"]


class GPSConfig:
    ENABLE_KEY = "enable"
    SERIAL_DEV_KEY = "serial_dev"
    BAUD_RATE_KEY = "baud_rate"
    INIT_TIMEOUT_KEY = "init_timeout"

    """
    aqi config data
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
    def enable(self) -> bool:
        """
        enable property getter
        :param self: this
        :return: the enable
        """
        return self.__dict__[GPSConfig.ENABLE_KEY]

    @property
    def serialDevice(self):
        """
        serialDevice property getter
        :param self: this
        :return: the serialDevice
        """
        return self.__dict__[GPSConfig.SERIAL_DEV_KEY]

    @property
    def baudRate(self) -> int:
        """
        baudRate property getter
        :param self: this
        :return: the baudRate
        """
        return self.__dict__[GPSConfig.BAUD_RATE_KEY]

    @property
    def initTimeout(self) -> int:
        """
        initTimeout property getter
        :param self: this
        :return: the initTimeout
        """
        return self.__dict__[GPSConfig.INIT_TIMEOUT_KEY]
