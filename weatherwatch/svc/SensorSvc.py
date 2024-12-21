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
        """
        ctor
        :param self: this
        """

        self._sdr_reader: SDRReader = SDRReader()
        self._bmp_reader: Bmp388SensorReader = Bmp388SensorReader()
        self._indoor_repo: IndoorSensorRepository = IndoorSensorRepository()
        self._outdoor_repo: OutdoorSensorRepository = OutdoorSensorRepository()

        EventBus.subscribe(IndoorData.__name__, self.handle_indoor)
        EventBus.subscribe(OutdoorData.__name__, self.handle_outdoor)

    def process(self):
        """
        service entry point
        :param self: this
        """
        self.logger.info("processing sensors")

        self._sdr_reader.read()

        self.logger.info("processing complete")

    def handle_indoor(self, data: IndoorData):
        """
        process indoor sensor data
        :param self: this
        """
        self.logger.debug("processing %s", IndoorData.__name__)

        try:
            ent: IndoorSensor = IndoorSensor()
            self.set_base_data(data, ent)

            ent.channel = data.channel

            self._indoor_repo.insert(ent)
        except Exception:
            self.logger.exception("failed to insert %s", data)

    def handle_outdoor(self, data: OutdoorData):
        """
        process outdoor sensor data
        :param self: this
        """
        self.logger.debug("processing %s", OutdoorData.__name__)
        self.logger.debug("read %s", data)

        try:
            last_read: OutdoorSensor = self._outdoor_repo.find_latest()
            self.logger.debug("last %s", last_read)

            ent: OutdoorSensor = OutdoorSensor()
            self.set_base_data(data, ent)

            bmp = self._bmp_reader.read()
            ent.pressure = bmp.pressure

            ent.rain_cum_mm = data.rain_mm

            delta: Decimal = 0.0

            if last_read is not None:  # edge will happen with new DB
                delta = round(Decimal(str(data.rain_mm)) - last_read.rain_cum_mm, 2)

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

            self._outdoor_repo.insert(ent)
        except Exception:
            self.logger.exception("failed to insert %s", data)

    def set_base_data(self, data: BaseData, ent: BaseSensor):
        """
        set sensor base data on entity
        :param self: this
        :param data: base data
        :param ent: the base entity
        """
        ent.temperature_f = data.temperature
        ent.humidity = data.humidity
        ent.sensor_id = data.sensor_id
        ent.battery_ok = data.battery_ok
        ent.read_time = data.time_stamp
        ent.raw = data.raw
