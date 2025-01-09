from datetime import datetime

from util.Logger import logger

__all__ = ["WUData"]


@logger
class WUData:
    """
    post data to weather underground
    https://support.weather.com/s/article/PWS-Upload-Protocol?language=en_US
    """

    AQI_AQPM2_5_KEY = "aqpm2.5"
    AQI_AQPM10_KEY = "aqpm10"

    # names are driven by wu api
    # pylint: disable=invalid-name
    def __init__(
        self,
        winddir: int,
        windspeedmph,
        windgustmph,
        humidity,
        dewptf,
        tempf,
        dailyrainin,
        baromin,
        solarradiation,
        uv,
        indoortempf,
        indoorhumidity,
    ):
        """
        ctor
        :param self: this
        """
        self.action = "updateraw"
        self.ID = None
        self.PASSWORD = None
        self.dateutc = None

        self.winddir = str(winddir)
        self.windspeedmph = str(windspeedmph)
        self.windgustmph = str(windgustmph)
        self.humidity = str(humidity)
        self.dewptf = str(dewptf)
        self.tempf = str(tempf)
        self.dailyrainin = str(dailyrainin)
        self.baromin = str(baromin)
        self.solarradiation = str(solarradiation)
        self.UV = str(uv)
        self.indoortempf = str(indoortempf)
        self.indoorhumidity = str(indoorhumidity)

    def station_id(self, station_id: str):
        """
        set station id
        :param self: this
        :param station_id: the wu station id
        """
        self.ID = station_id

    def station_key(self, station_key: str):
        """
        set station key
        :param self: this
        :param station_key: the wu station key
        """
        self.PASSWORD = station_key

    def read_time(self, read_time: datetime):
        """
        set sensor read time
        :param self: this
        :param read_time: the sensor read time
        """
        self.dateutc = read_time.strftime("%Y-%m-%d %H:%M:%S")

    def aqpm2_5(self, aqpm2_5):
        """
        set aqi aqpm2_5
        :param self: this
        :param aqpm2_5: aqi aqpm2_5
        """
        setattr(self, WUData.AQI_AQPM2_5_KEY, aqpm2_5)

    def aqpm10(self, aqpm10):
        """
        set aqi aqpm10
        :param self: this
        :param aqpm10: aqi aqpm10
        """
        setattr(self, WUData.AQI_AQPM10_KEY, aqpm10)
