from util.Logger import logger

__all__ = ["GPSConfig"]


@logger
class GPSConfig:
    """
    gps config data
    """
    ENABLE_KEY = "enable"
    SERIAL_DEV_KEY = "serial_dev"
    BAUD_RATE_KEY = "baud_rate"
    INIT_TIMEOUT_KEY = "init_timeout"


    def __init__(self, config: dict):
        """
        ctor
        :param self: this
        """

        for key in config:
            self.__dict__[key] = config[key]

    @property
    def enable(self) -> bool:
        """
        enable property getter
        :param self: this
        :return: the enable
        """
        return self.__dict__[GPSConfig.ENABLE_KEY]

    @property
    def serial_device(self):
        """
        serialDevice property getter
        :param self: this
        :return: the serialDevice
        """
        return self.__dict__[GPSConfig.SERIAL_DEV_KEY]

    @property
    def baud_rate(self) -> int:
        """
        baudRate property getter
        :param self: this
        :return: the baudRate
        """
        return self.__dict__[GPSConfig.BAUD_RATE_KEY]

    @property
    def init_timeout(self) -> int:
        """
        initTimeout property getter
        :param self: this
        :return: the initTimeout
        """
        return self.__dict__[GPSConfig.INIT_TIMEOUT_KEY]
