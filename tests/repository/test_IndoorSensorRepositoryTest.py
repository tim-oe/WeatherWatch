import unittest

import datetime

import json

from weatherwatch.repository.IndoorSensorRepository import IndoorSensorRepository
from weatherwatch.entity.IndoorSensor import IndoorSensor
from weatherwatch.sensor.sdr.IndoorData import IndoorData

class IndoorSensorRepositoryTest(unittest.TestCase):

    def test(self):
        
        repo: IndoorSensorRepository = IndoorSensorRepository()

        repo.exec('truncate ' + IndoorSensor.__tablename__)

        with open("tests/data/indoor.json", "r") as file:
            j = json.load(file)

        with open("tests/data/indoor.json", "r") as file:
            data: IndoorData = json.load(file, object_hook=IndoorData.jsonDecoder)
            
        ent: IndoorSensor = IndoorSensor()
        ent.channel = data.channel
        ent.temperature_f = data.temperature
        ent.humidity = data.humidity
        ent.sensor_id = data.id
        ent.battery_ok = data.batteryOk
        ent.read_time = datetime.datetime.now()
        ent.raw = j

        repo.insert(ent)
        
        print(str(ent))
        
        self.assertIsNotNone(ent.id)
        act = repo.findById(ent.id)
        self.assertIsNotNone(act)
        self.assertEqual(ent.id, act.id)

        act = repo.findLatest(ent.channel)
        self.assertIsNotNone(act)
        self.assertEqual(ent.id, act.id)
