__all__ = ["WUSvc"]


from datetime import date

from conf.AppConfig import AppConfig
from conf.WUConfig import WUConfig
from entity.IndoorSensor import IndoorSensor
from entity.OutdoorSensor import OutdoorSensor
from py_singleton import singleton
from repository.IndoorSensorRepository import IndoorSensorRepository
from repository.OutdoorSensorRepository import OutdoorSensorRepository
from util.Converter import Converter
from util.Logger import logger
from wu.WUClient import WUClient
from wu.WUData import WUData


@logger
@singleton
class WUSvc:
    """
    weather underground service
    1) read latest outdoor and indoor sensor
    2) post data to weather underground
    """

    def __init__(self):

        self._client: WUClient = WUClient()
        self._config: WUConfig = AppConfig().wu
        self._indoorRepo: IndoorSensorRepository = IndoorSensorRepository()
        self._outdoorRepo: OutdoorSensorRepository = OutdoorSensorRepository()

    def process(self):
        self.logger.info("processing weather underground upload")
        try:
            inData: IndoorSensor = self._indoorRepo.findLatest(self._config.indoorchannelKey)
            rainFail_mm = float(self._outdoorRepo.getDaysRainfall(date.today()))

            outData: OutdoorSensor = self._outdoorRepo.findLatest()

            data: WUData = WUData(
                winddir=outData.wind_dir_deg,
                windspeedmph=round(Converter.mps_to_mph(outData.wind_avg_m_s), 2),
                windgustmph=round(Converter.mps_to_mph(outData.wind_max_m_s), 2),
                humidity=outData.humidity,
                tempf=round(outData.temperature_f, 2),
                dailyrainin=round(Converter.mm_to_inch(rainFail_mm), 2),
                baromin=round(Converter.hpa_to_iom(outData.pressure), 2),
                solarradiation=round(Converter.lux_to_wpm(outData.light_lux), 2),
                uv=outData.uv,
                indoortempf=round(inData.temperature_f, 2),
                indoorhumidity=inData.humidity,
            )

            self._client.post(outData.read_time, data)
        except Exception:
            self.logger.exception("failed to upload data to weather underground")
