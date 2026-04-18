from util.Logger import logger

__all__ = ["MqttConfig"]


@logger
class MqttConfig:
    """
    mqtt config data
    """

    ENABLE_KEY = "enable"
    HOST_KEY = "host"
    PORT_KEY = "port"
    USERNAME_KEY = "username"
    PASSWORD_KEY = "password"
    TOPICS_KEY = "topics"
    SOLAR_KEY = "solar"
    TEMPERATURE_KEY = "temperature"

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
        return self.__dict__[MqttConfig.ENABLE_KEY]

    @property
    def host(self) -> str:
        """
        host property getter
        :param self: this
        :return: the host
        """
        return self.__dict__[MqttConfig.HOST_KEY]

    @property
    def port(self) -> int:
        """
        port property getter
        :param self: this
        :return: the port
        """
        return self.__dict__[MqttConfig.PORT_KEY]

    @property
    def username(self) -> str:
        """
        username property getter
        :param self: this
        :return: the username
        """
        return self.__dict__[MqttConfig.USERNAME_KEY]

    @property
    def password(self) -> str:
        """
        password property getter
        :param self: this
        :return: the password
        """
        return self.__dict__[MqttConfig.PASSWORD_KEY]

    @property
    def solar_topic(self) -> str:
        """
        solar topic property getter
        :param self: this
        :return: the solar topic
        """
        return self.__dict__[MqttConfig.TOPICS_KEY][MqttConfig.SOLAR_KEY]

    @property
    def temperature_topic(self) -> str:
        """
        temperature topic property getter
        :param self: this
        :return: the temperature topic
        """
        return self.__dict__[MqttConfig.TOPICS_KEY][MqttConfig.TEMPERATURE_KEY]
