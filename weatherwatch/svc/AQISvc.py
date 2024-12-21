import time
from datetime import datetime

from conf.AppConfig import AppConfig
from conf.AQIConfig import AQIConfig
from entity.AQISensor import AQISensor
from py_singleton import singleton
from repository.AQISensorRepository import AQISensorRepository
from sensor.aqi.Hm3301Data import Hm3301Data
from sensor.aqi.Hm3301Reader import Hm3301Reader
from util.Converter import Converter
from util.Logger import logger

__all__ = ["AQISvc"]


@logger
@singleton
class AQISvc:
    """
    aqi service
    this does the sensor processing
    1) reads aqi data
    2) write data to datastore
    """

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._hm_3301_reader: Hm3301Reader = Hm3301Reader()
        self._config: AQIConfig = AppConfig().aqi
        self._repo: AQISensorRepository = AQISensorRepository()

    def process(self):
        """
        process sensor
        :param self: this
        """
        self.logger.info("processing aqi")
        start = datetime.now()

        try:
            data: Hm3301Data = self.read()

            ent: AQISensor = AQISensor()

            ent.pm_1_0_conctrt_std = data.pm_1_0_conctrt_std
            ent.pm_2_5_conctrt_std = data.pm_2_5_conctrt_std
            ent.pm_10_conctrt_std = data.pm_10_conctrt_std

            ent.pm_1_0_conctrt_atmosph = data.pm_1_0_conctrt_atmosph
            ent.pm_2_5_conctrt_atmosph = data.pm_2_5_conctrt_atmosph
            ent.pm_10_conctrt_atmosph = data.pm_10_conctrt_atmosph

            ent.read_time = datetime.now()

            self._repo.insert(ent)
            self.logger.info("AQI processing complete  duration %s", Converter.duration_seconds(start))
        except Exception:
            self.logger.exception("failed to process aqi data")

    def read(self) -> Hm3301Data:
        """
        read sensor
        :param self: this
        :return: sensor read data
        getting intermintent bad data so
        trying to kludge it by doing mutliple reads
        and take the lowest values of each metric
        """
        d: Hm3301Data = self._hm_3301_reader.read()

        if d.high():
            for x in range(self._config.poll):
                time.sleep(2)
                d.lower(self._hm_3301_reader.read())
                if d.high() is False:
                    break

        return d

    # def cleanup(self):
    #     """
    #     kludge for funy data....
    #     """

    #     self._repo.clean()
