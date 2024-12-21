from decimal import Decimal

from entity.BaseSensor import BaseSensor
from entity.IndoorSensor import IndoorSensor
from entity.OutdoorSensor import OutdoorSensor
from py_singleton import singleton
from python_event_bus import EventBus
from repository.IndoorSensorRepository import IndoorSensorRepository
from repository.OutdoorSensorRepository import OutdoorSensorRepository
from sensor.bmp.Bmp388SensorReader import Bmp388SensorReader
from sensor.sdr.BaseData import BaseData
from sensor.sdr.IndoorData import IndoorData
from sensor.sdr.OutdoorData import OutdoorData
from sensor.sdr.SDRReader import SDRReader
from util.Logger import logger

__all__ = ["SensorSvc"]


@logger
@singleton
class SensorSvc:
    """
    sensor service
    this does the sensor processing
    1) read data from sensors
    2) write data to datastore
    """

    def __init__(self):

        self._sdrReader: SDRReader = SDRReader()
        self._bmpReader: Bmp388SensorReader = Bmp388SensorReader()
        self._indoorRepo: IndoorSensorRepository = IndoorSensorRepository()
        self._outdoorRepo: OutdoorSensorRepository = OutdoorSensorRepository()

        EventBus.subscribe(IndoorData.__name__, self.handleIndoor)
        EventBus.subscribe(OutdoorData.__name__, self.handleOutdoor)

    def process(self):
        self.logger.info("processing sensors")

        self._sdrReader.read()

        self.logger.info("processing complete")

    def handleIndoor(self, data: IndoorData):
        self.logger.debug("processing %s", IndoorData.__name__)

        try:
            ent: IndoorSensor = IndoorSensor()
            self.setBaseData(data, ent)

            ent.channel = data.channel

            self._indoorRepo.insert(ent)
        except Exception:
            self.logger.exception("failed to insert %s", data)

    def handleOutdoor(self, data: OutdoorData):
        self.logger.debug("processing %s", OutdoorData.__name__)
        self.logger.debug("read %s", data)

        try:
            lastRead: OutdoorSensor = self._outdoorRepo.find_latest()
            self.logger.debug("last %s", lastRead)

            ent: OutdoorSensor = OutdoorSensor()
            self.setBaseData(data, ent)

            bmp = self._bmpReader.read()
            ent.pressure = bmp.pressure

            ent.rain_cum_mm = data.rain_mm

            delta: Decimal = 0.0

            if lastRead is not None:  # edge will happen with new DB
                delta = round(Decimal(str(data.rain_mm)) - lastRead.rain_cum_mm, 2)

            self.logger.debug("calc delta %s", delta)

            if delta < Decimal(0.0):  # edge case sensor reset
                ent.rain_delta_mm = round(data.rain_mm, 2)
            else:
                ent.rain_delta_mm = delta

            self.logger.debug("rain delta %s", ent.rain_delta_mm)

            ent.wind_avg_m_s = data.wind_avg_m_s
            ent.wind_max_m_s = data.wind_max_m_s
            ent.wind_dir_deg = data.wind_dir_deg
            ent.light_lux = data.light_lux
            ent.uv = data.uv

            self._outdoorRepo.insert(ent)
        except Exception:
            self.logger.exception("failed to insert %s", data)

    def setBaseData(self, data: BaseData, ent: BaseSensor):
        ent.temperature_f = data.temperature
        ent.humidity = data.humidity
        ent.sensor_id = data.sensor_id
        ent.battery_ok = data.battery_ok
        ent.read_time = data.time_stamp
        ent.raw = data.raw
