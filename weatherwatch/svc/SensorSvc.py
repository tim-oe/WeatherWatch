import decimal
import logging

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

__all__ = ["SensorSvc"]


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
        logging.info("processing sensors")

        self._sdrReader.read()

        logging.info("processing complete")

    def handleIndoor(self, data: IndoorData):
        logging.debug("processing %s", IndoorData.__name__)

        try:
            ent: IndoorSensor = IndoorSensor()
            self.setBaseData(data, ent)

            ent.channel = data.channel

            self._indoorRepo.insert(ent)
        except Exception:
            logging.exception("failed to insert %s", data)

    def handleOutdoor(self, data: OutdoorData):
        logging.debug("processing %s", OutdoorData.__name__)
        logging.debug("read %s", data)
        
        try:
            lastRead: OutdoorSensor = self._outdoorRepo.findLatest()
            logging.debug("last %s", lastRead)

            ent: OutdoorSensor = OutdoorSensor()
            self.setBaseData(data, ent)

            bmp = self._bmpReader.read()
            ent.pressure = bmp.pressure

            ent.rain_cum_mm = data.rain_mm

            delta: Decimal = 0.0

            logging.debug("data rain %s %s", type(data.rain_mm), data.rain_mm)

            if lastRead is not None:  # edge will happen with new DB
                logging.debug("last rain %s %s", type(lastRead.rain_cum_mm), lastRead.rain_cum_mm)
                delta = Decimal(str(data.rain_mm)) - lastRead.rain_cum_mm

            logging.debug("calc delta %s", delta)

            if delta < Decimal(0.0):  # edge case sensor reset
                ent.rain_delta_mm = data.rain_mm
            else:
                ent.rain_delta_mm = delta

            logging.info("rain delta %s", ent.rain_delta_mm)

            ent.wind_avg_m_s = data.wind_avg_m_s
            ent.wind_max_m_s = data.wind_max_m_s
            ent.wind_dir_deg = data.wind_dir_deg
            ent.light_lux = data.light_lux
            ent.uv = data.uv

            self._outdoorRepo.insert(ent)
        except Exception:
            logging.exception("failed to insert %s", data)

    def setBaseData(self, data: BaseData, ent: BaseSensor):
        ent.temperature_f = data.temperature
        ent.humidity = data.humidity
        ent.sensor_id = data.id
        ent.battery_ok = data.batteryOk
        ent.read_time = data.timeStamp
        ent.raw = data.raw
