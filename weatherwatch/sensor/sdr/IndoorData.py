from sensor.sdr.BaseData import BaseData

__all__ = ["IndoorData"]


class IndoorData(BaseData):
    TEMP_KEY = "temperature_F"
    HUMID_KEY = "humidity"

    """
    indoor sensor data
    """

    def __init__(self, channel=None):
        """
        ctor
        :param self: this
        """
        self._channel = channel

        super().__init__()

    @staticmethod
    def jsonDecoder(d: dict) -> "IndoorData":
        try:
            data = IndoorData()
            BaseData.baseDecoder(data, d)
            data.channel = int(d[BaseData.CHANNEL_KEY])
            data.temperature = d[IndoorData.TEMP_KEY]
            data.humidity = d[IndoorData.HUMID_KEY]
            return data
        except Exception as e:
            raise Exception("failed to parse " + str(d)) from e

    @property
    def channel(self) -> int:
        """
        channel property getter
        :param self: this
        :return: the channel
        """
        return self._channel

    @channel.setter
    def channel(self, channel: int):
        """
        channel property setter
        :param self: this
        :param: the channel
        """
        self._channel = channel

    @property
    def temperature(self):
        """
        temperature string property getter
        :param self: this
        :return: the temperature
        """
        return self._temperature

    @temperature.setter
    def temperature(self, temperature):
        """
        temperature property setter
        :param self: this
        :param: the temperature
        """
        self._temperature = temperature

    @property
    def humidity(self):
        """
        humidity string property getter
        :param self: this
        :return: the humidity
        """
        return self._humidity

    @humidity.setter
    def humidity(self, humidity):
        """
        humidity property setter
        :param self: this
        :param: the humidity
        """
        self._humidity = humidity
