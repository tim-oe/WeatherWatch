from util.Logger import logger

__all__ = ["AQIConfig"]


@logger
class AQIConfig:
    """
    aqi config data
    """

    ENABLE_KEY = "enable"
    RETRY_KEY = "retry"
    POLL_KEY = "poll"
    WAIT_SEC_KEY = "wait_sec"

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
        return self.__dict__[AQIConfig.ENABLE_KEY]

    @property
    def retry(self) -> int:
        """
        retry property getter
        :param self: this
        :return: the retry
        """
        return self.__dict__[AQIConfig.RETRY_KEY]

    @property
    def poll(self) -> int:
        """
        poll property getter
        :param self: this
        :return: the poll
        """
        return self.__dict__[AQIConfig.POLL_KEY]

    @property
    def wait_sec(self) -> int:
        """
        wait_sec property getter
        :param self: this
        :return: the wait_sec property
        """
        return self.__dict__[AQIConfig.WAIT_SEC_KEY]
