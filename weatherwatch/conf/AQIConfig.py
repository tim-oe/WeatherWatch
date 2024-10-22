__all__ = ["AQIConfig"]


class AQIConfig:
    ENABLE_KEY = "enable"
    RETRY_KEY = "retry"

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
        return self.__dict__[AQIConfig.ENABLE_KEY]

    @property
    def retry(self) -> int:
        """
        retry property getter
        :param self: this
        :return: the retry
        """
        return self.__dict__[AQIConfig.RETRY_KEY]
