from pathlib import Path

__all__ = ["DashConfig"]


class DashConfig:
    HOST_KEY = "host"
    PORT_KEY = "port"
 
    """
    dash app config data
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
