__all__ = ["WUSvc"]


from datetime import date

from conf.AppConfig import AppConfig
from conf.AQIConfig import AQIConfig
from conf.WUConfig import WUConfig
from entity.AQISensor import AQISensor
from entity.IndoorSensor import IndoorSensor
from entity.OutdoorSensor import OutdoorSensor
from py_singleton import singleton
from repository.AQISensorRepository import AQISensorRepository
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
        self._aqiConfig: AQIConfig = AppConfig().aqi
        self._config: WUConfig = AppConfig().wu
        self._indoorRepo: IndoorSensorRepository = IndoorSensorRepository()
        self._outdoorRepo: OutdoorSensorRepository = OutdoorSensorRepository()
        self._aqiRepo: AQISensorRepository = AQISensorRepository()

    def process(self):
        self.logger.info("processing weather underground upload")
        try:
            inData: IndoorSensor = self._indoorRepo.find_latest(self._config.indoor_channel_key)
            rainFail_mm = float(self._outdoorRepo.get_days_rainfall(date.today()))

            outData: OutdoorSensor = self._outdoorRepo.find_latest()

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

            self.setAQI(data)

            self._client.post(outData.read_time, data)
        except Exception:
            self.logger.exception("failed to upload data to weather underground")

    def setAQI(self, data: WUData):
        if self._aqiConfig.enable:
            aqiData: AQISensor = self._aqiRepo.find_latest()
            data.aqpm2_5(aqiData.pm_2_5_conctrt_std)
            data.aqpm10(aqiData.pm_1_0_conctrt_std)
