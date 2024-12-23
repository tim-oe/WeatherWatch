from util.Logger import logger

__all__ = ["WUConfig"]


@logger
class WUConfig:
    """
    weather underground config data
    """

    ENABLE_KEY = "enable"
    STATION_ID_KEY = "station_id"
    STATION_KEY_KEY = "station_key"
    API_KEY_KEY = "api_key"
    RETRIES_KEY = "retries"
    INDOOR_CHANNEL_KEY = "indoor_channel"

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
        return self.__dict__[WUConfig.ENABLE_KEY]

    @property
    def retries(self) -> int:
        """
        retries property getter
        :param self: this
        :return: the retries
        """
        return self.__dict__[WUConfig.RETRIES_KEY]

    @property
    def station_id(self):
        """
        stationId property getter
        :param self: this
        :return: the stationId
        """
        return self.__dict__[WUConfig.STATION_ID_KEY]

    @property
    def station_key(self):
        """
        stationKey property getter
        :param self: this
        :return: the stationKey
        """
        return self.__dict__[WUConfig.STATION_KEY_KEY]

    @property
    def api_key(self):
        """
        apiKey property getter
        :param self: this
        :return: the apiKey
        """
        return self.__dict__[WUConfig.API_KEY_KEY]

    @property
    def indoor_channel(self) -> int:
        """
        indoorchannel property getter
        :param self: this
        :return: the indoorchannel
        """
        return self.__dict__[WUConfig.INDOOR_CHANNEL_KEY]
