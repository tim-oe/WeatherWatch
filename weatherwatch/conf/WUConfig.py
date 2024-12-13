__all__ = ["WUConfig"]


from util.Logger import logger


@logger
class WUConfig:
    ENABLE_KEY = "enable"
    STATION_ID = "station_id"
    STATION_KEY = "station_key"
    API_KEY = "api_key"
    RETRIES_KEY = "retries"
    INDOOR_CHANNEL_KEY = "indoor_channel"

    """
    weather underground config data
    """

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
    def stationId(self):
        """
        stationId property getter
        :param self: this
        :return: the stationId
        """
        return self.__dict__[WUConfig.STATION_ID]

    @property
    def stationKey(self):
        """
        stationKey property getter
        :param self: this
        :return: the stationKey
        """
        return self.__dict__[WUConfig.STATION_KEY]

    @property
    def apiKey(self):
        """
        apiKey property getter
        :param self: this
        :return: the apiKey
        """
        return self.__dict__[WUConfig.API_KEY]

    @property
    def indoorchannelKey(self) -> int:
        """
        indoorchannel property getter
        :param self: this
        :return: the indoorchannel
        """
        return self.__dict__[WUConfig.INDOOR_CHANNEL_KEY]
