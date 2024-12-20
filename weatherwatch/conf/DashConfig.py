from util.Logger import logger

__all__ = ["DashConfig"]


@logger
class DashConfig:
    """
    dash app config data
    """

    HOST_KEY = "host"
    PORT_KEY = "port"
    DEBUG_KEY = "debug"

    def __init__(self, config: dict):
        """
        ctor
        :param self: this
        """

        for key in config:
            self.__dict__[key] = config[key]

    @property
    def host(self) -> str:
        """
        host property getter
        :param self: this
        :return: the host
        """
        return self.__dict__[DashConfig.HOST_KEY]

    @property
    def port(self) -> int:
        """
        port property getter
        :param self: this
        :return: the port
        """
        return self.__dict__[DashConfig.PORT_KEY]

    @property
    def debug(self) -> bool:
        """
        debug property getter
        :param self: this
        :return: the debug
        """
        return self.__dict__[DashConfig.DEBUG_KEY]
