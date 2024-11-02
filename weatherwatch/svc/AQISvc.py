import datetime
import logging
import time

from conf.AppConfig import AppConfig
from conf.AQIConfig import AQIConfig
from entity.AQISensor import AQISensor
from py_singleton import singleton
from repository.AQISensorRepository import AQISensorRepository
from sensor.aqi.Hm3301Data import Hm3301Data
from sensor.aqi.Hm3301Reader import Hm3301Reader

__all__ = ["AQISvc"]


@singleton
class AQISvc:
    """
    sensor service
    this does the sensor processing
    1) read data from sensors
    2) write data to datastore
    """

    def __init__(self):

        self._hm3301Reader: Hm3301Reader = Hm3301Reader()
        self._config: AQIConfig = AppConfig().aqi
        self._repo: AQISensorRepository = AQISensorRepository()

    def process(self):
        logging.info("processing aqi")
        start = datetime.datetime.now()

        try:
            data: Hm3301Data = self.read()

            ent: AQISensor = AQISensor()

            ent.pm_1_0_conctrt_std = data.pm_1_0_conctrt_std
            ent.pm_2_5_conctrt_std = data.pm_2_5_conctrt_std
            ent.pm_10_conctrt_std = data.pm_10_conctrt_std

            ent.pm_1_0_conctrt_atmosph = data.pm_1_0_conctrt_atmosph
            ent.pm_2_5_conctrt_atmosph = data.pm_2_5_conctrt_atmosph
            ent.pm_10_conctrt_atmosph = data.pm_10_conctrt_atmosph

            ent.read_time = datetime.datetime.now()

            self._repo.insert(ent)
            logging.info("AQI processing complete  duration %s", self.duration(start))
        except Exception:
            logging.exception("failed to process aqi data")

    def read(self) -> Hm3301Data:
        """
        getting intermintent bad data so
        trying to kludge it by doing mutliple reads
        and take the lowest values of each metric
        """
        d: Hm3301Data = self._hm3301Reader.read()

        if d.high():
            for x in range(self._config.poll):
                time.sleep(2)
                d.lower(self._hm3301Reader.read())
                if d.high() is False:
                    break

        return d

    def duration(self, start: datetime) -> int:
        """
        calculate the execution duration from start to now
        """
        current = datetime.datetime.now()
        return int((current - start).total_seconds())

    def cleanup(self):
        """
        kludge for funy data....
        """

        self._repo.clean()
