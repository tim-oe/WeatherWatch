import datetime
import logging

from py_singleton import singleton

from entity.AQISensor import AQISensor
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
        self._repo: AQISensorRepository = AQISensorRepository()


    def process(self):
        logging.info("processing aqi")

        try:
            data: Hm3301Data = self._hm3301Reader.read()

            ent: AQISensor = AQISensor()

            ent.pm_1_0_conctrt_std = data.pm_1_0_conctrt_std
            ent.pm_2_5_conctrt_std = data.pm_2_5_conctrt_std
            ent.pm_10_conctrt_std = data.pm_10_conctrt_std

            ent.pm_1_0_conctrt_atmosph = data.pm_1_0_conctrt_atmosph
            ent.pm_2_5_conctrt_atmosph = data.pm_2_5_conctrt_atmosph
            ent.pm_10_conctrt_atmosph = data.pm_10_conctrt_atmosph
            
            ent.read_time = datetime.datetime.now()

            self._repo.insert(ent)
            logging.info("processing aqi complete")
        except Exception:
            logging.exception("failed to process aqi data")
