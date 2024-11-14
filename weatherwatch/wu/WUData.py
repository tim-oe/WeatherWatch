from datetime import datetime

from util.Logger import logger

__all__ = ["WUData"]


@logger
class WUData:
    """
    post data to weather underground
    https://support.weather.com/s/article/PWS-Upload-Protocol?language=en_US
    """

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
