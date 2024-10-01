import unittest

import datetime

import json

from src.repository.OutdoorSensorRepository import OutdoorSensorRepository
from src.entity.OutdoorSensor import OutdoorSensor
from src.sensor.sdr.OutdoorData import OutdoorData

class OutdoorSensorRepositoryTest(unittest.TestCase):

    def test(self):
        
        repo: OutdoorSensorRepository = OutdoorSensorRepository()

        with open("tests/data/outdoor.json", "r") as file:
            j = json.load(file)

        with open("tests/data/outdoor.json", "r") as file:
            data: OutdoorData = json.load(file, object_hook=OutdoorData.jsonDecoder)
            
        ent: OutdoorSensor = OutdoorSensor()
        ent.model = data.model
        ent.temperature_f = data.temperature
        ent.humidity = data.humidity
        ent.rain_mm = data.rain_mm
        ent.wind_avg_m_s = data.wind_avg_m_s
        ent.wind_max_m_s = data.wind_max_m_s
        ent.wind_dir_deg = data.wind_dir_deg
        ent.light_lux = data.light_lux
        ent.uv = data.uv
        ent.sensor_id = data.id
        ent.battery_ok = data.batteryOk
        ent.read_time = datetime.datetime.now()
        # comes from BMP sensor
        ent.pressure = 999.99
        ent.mic = data.mic
        ent.mod = data.mod
        ent.freq = data.freq
        ent.noise = data.noise
        ent.rssi = data.rssi
        ent.snr = data.snr
        ent.raw = j

        repo.insert(ent)
        
        self.assertIsNotNone(ent.id)
        act = repo.findById(ent.id)
        self.assertIsNotNone(act)
        # TODO not working...
        #self.assertEquals(ent, act)
        
