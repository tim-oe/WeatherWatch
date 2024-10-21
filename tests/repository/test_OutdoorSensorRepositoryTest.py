import unittest

import datetime

import json

from repository.BaseRepository import BaseRepository
from tests.repository.BaseRepositoryTest import BaseRespositoryTest
from weatherwatch.repository.OutdoorSensorRepository import OutdoorSensorRepository
from weatherwatch.entity.OutdoorSensor import OutdoorSensor
from weatherwatch.sensor.sdr.OutdoorData import OutdoorData

class OutdoorSensorRepositoryTest(BaseRespositoryTest):

    def getRepo(self) -> BaseRepository:
        return OutdoorSensorRepository()

    def test(self):
        
        repo: OutdoorSensorRepository = self.getRepo()

        with open("tests/data/outdoor.json", "r") as file:
            j = json.load(file)

        with open("tests/data/outdoor.json", "r") as file:
            data: OutdoorData = json.load(file, object_hook=OutdoorData.jsonDecoder)
            
        ent: OutdoorSensor = OutdoorSensor()
        ent.sensor_id = data.id
        ent.battery_ok = data.batteryOk
        ent.read_time = datetime.datetime.now()
        ent.temperature_f = data.temperature
        ent.humidity = data.humidity
        ent.rain_mm = data.rain_mm
        ent.wind_avg_m_s = data.wind_avg_m_s
        ent.wind_max_m_s = data.wind_max_m_s
        ent.wind_dir_deg = data.wind_dir_deg
        ent.light_lux = data.light_lux
        ent.uv = data.uv
        # comes from BMP sensor
        ent.pressure = 999.99
        ent.raw = j

        repo.insert(ent)
        
        self.assertIsNotNone(ent.id)
        print(str(ent))

        act = repo.findById(ent.id)
        self.assertIsNotNone(act)
        self.assertEqual(ent.id, act.id)
        self.assertEqual(ent.read_time, act.read_time)

        act = repo.findLatest()
        self.assertIsNotNone(act)
        self.assertEqual(ent.id, act.id)
        self.assertEqual(ent.read_time, act.read_time)
        
