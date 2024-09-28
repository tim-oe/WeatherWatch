import logging
from typing import List

from conf.AppConfig import AppConfig
from entity.BaseSensor import BaseSensor
from entity.IndoorSensor import IndoorSensor
from entity.OutdoorSensor import OutdoorSensor
from repository.IndoorSensorRepository import IndoorSensorRepository
from repository.OutdoorSensorRepository import OutdoorSensorRepository
from sensor.bmp.Bmp388SensorReader import Bmp388SensorReader
from sensor.bmp.BMPData import BMPData
from sensor.sdr.BaseData import BaseData
from sensor.sdr.IndoorData import IndoorData
from sensor.sdr.OutdoorData import OutdoorData
from sensor.sdr.SDRReader import SDRReader

__all__ = ["AppConfig"]


class SensorSvc(object):
    """
    sensor service
    this does the sensor processing
    1) read data from sensors
    2) write data to datastore
    """

    # override for singleton
    # https://www.geeksforgeeks.org/singleton-pattern-in-python-a-complete-guide/
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(SensorSvc, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self._appConfig: AppConfig = AppConfig()
        self._sdrReader: SDRReader = SDRReader()
        self._bmpReader: Bmp388SensorReader = Bmp388SensorReader()
        self._indoorRepo: IndoorSensorRepository = IndoorSensorRepository()
        self._outdoorRepo: OutdoorSensorRepository = OutdoorSensorRepository()

    def process(self):
        logging.info("processing sensors")

        self._sdrReader.read()

        reads: List[BaseData] = self._sdrReader.reads
        logging.info("sensor cnt: " + str(len(reads)))

        for d in reads:
            try:
                match d.config.dataClass:
                    case IndoorData.__name__:
                        self._indoorRepo.insert(self.toIndoor(d))
                    case OutdoorData.__name__:
                        self._outdoorRepo.insert(self.toOutdoor(d, self._bmpReader.read()))
                    case _:
                        logging.error("unkown impl for sensor: " + d)
            except Exception as e:
                logging.error("failed to proces " + str(d) + "\n" + str(e))

        logging.info("processing complete")

    def toIndoor(self, data: IndoorData) -> IndoorSensor:
        ent: IndoorSensor = IndoorSensor()
        self.setBaseData(data, ent)

        ent.channel = data.channel

        return ent

    def toOutdoor(self, data: OutdoorData, bmp: BMPData) -> OutdoorSensor:
        ent: OutdoorSensor = OutdoorSensor()
        self.setBaseData(data, ent)

        ent.pressure = bmp.pressure

        ent.rain_mm = data.rain_mm
        ent.wind_avg_m_s = data.wind_avg_m_s
        ent.wind_max_m_s = data.wind_max_m_s
        ent.wind_dir_deg = data.wind_dir_deg
        ent.light_lux = data.light_lux
        ent.uv = data.uv

        return ent

    def setBaseData(self, data: BaseData, ent: BaseSensor):
        ent.model = data.model
        ent.temperature_f = data.temperature
        ent.humidity = data.humidity
        ent.sensor_id = data.id
        ent.battery_ok = data.batteryOk
        ent.read_time = data.timeStamp
        ent.mic = data.mic
        ent.mod = data.mod
        ent.freq = data.freq
        ent.noise = data.noise
        ent.rssi = data.rssi
        ent.snr = data.snr
        ent.raw = data.raw
