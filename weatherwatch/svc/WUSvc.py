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
        """
        ctor
        :param self: this
        """

        self._client: WUClient = WUClient()
        self._aqi_config: AQIConfig = AppConfig().aqi
        self._config: WUConfig = AppConfig().wu
        self._indoor_repo: IndoorSensorRepository = IndoorSensorRepository()
        self._outdoor_repo: OutdoorSensorRepository = OutdoorSensorRepository()
        self._aqi_repo: AQISensorRepository = AQISensorRepository()

    def process(self):
        """
        service entry point
        :param self: this
        """
        self.logger.info("processing weather underground upload")
        try:
            in_data: IndoorSensor = self._indoor_repo.find_latest(self._config.indoor_channel_key)
            rainfail_mm = float(self._outdoor_repo.get_days_rainfall(date.today()))

            out_data: OutdoorSensor = self._outdoor_repo.find_latest()

            data: WUData = WUData(
                winddir=out_data.wind_dir_deg,
                windspeedmph=round(Converter.mps_to_mph(out_data.wind_avg_m_s), 2),
                windgustmph=round(Converter.mps_to_mph(out_data.wind_max_m_s), 2),
                humidity=out_data.humidity,
                tempf=round(out_data.temperature_f, 2),
                dailyrainin=round(Converter.mm_to_inch(rainfail_mm), 2),
                baromin=round(Converter.hpa_to_iom(out_data.pressure), 2),
                solarradiation=round(Converter.lux_to_wpm(out_data.light_lux), 2),
                uv=out_data.uv,
                indoortempf=round(in_data.temperature_f, 2),
                indoorhumidity=in_data.humidity,
            )

            self.set_aqi(data)

            self._client.post(out_data.read_time, data)
        except Exception:
            self.logger.exception("failed to upload data to weather underground")

    def set_aqi(self, data: WUData):
        """
        set aqi data if enabled
        :param self: this
        :param data: the wu data
        """
        if self._aqi_config.enable:
            aqi_data: AQISensor = self._aqi_repo.find_latest()
            data.aqpm2_5(aqi_data.pm_2_5_conctrt_std)
            data.aqpm10(aqi_data.pm_1_0_conctrt_std)
