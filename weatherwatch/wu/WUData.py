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

    def __init__(
        self,
        winddir: int,
        windspeedmph,
        windgustmph,
        humidity,
        tempf,
        dailyrainin,
        baromin,
        solarradiation,
        uv,
        indoortempf,
        indoorhumidity,
    ):
        self.action = "updateraw"
        self.ID = None
        self.PASSWORD = None
        self.dateutc = None

        self.winddir = str(winddir)
        self.windspeedmph = str(windspeedmph)
        self.windgustmph = str(windgustmph)
        self.humidity = str(humidity)
        self.tempf = str(tempf)
        self.dailyrainin = str(dailyrainin)
        self.baromin = str(baromin)
        self.solarradiation = str(solarradiation)
        self.UV = str(uv)
        self.indoortempf = str(indoortempf)
        self.indoorhumidity = str(indoorhumidity)

    def stationId(self, stationId: str):
        self.ID = stationId

    def stationKey(self, stationKey: str):
        self.PASSWORD = stationKey

    def readTime(self, readTime: datetime):
        self.dateutc = readTime.strftime("%Y-%m-%d %H:%M:%S")

    def aqpm2_5(self, aqpm2_5):
        setattr(self, WUData.AQI_AQPM2_5_KEY, aqpm2_5)

    def aqpm10(self, aqpm10):
        setattr(self, WUData.AQI_AQPM10_KEY, aqpm10)
