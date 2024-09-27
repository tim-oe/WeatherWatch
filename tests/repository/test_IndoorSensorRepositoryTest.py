import unittest

import json

from src.repository.IndoorSensorRepository import IndoorSensorRepository
from src.entity.IndoorSensor import IndoorSensor
from sensor.sdr.IndoorData import IndoorData

class IndoorSensorRepositoryTest(unittest.TestCase):

    def test(self):
        
        repo: IndoorSensorRepository = IndoorSensorRepository()

        with open("tests/data/indoor.json", "r") as file:
            j = json.load(file)

        with open("tests/data/indoor.json", "r") as file:
            data: IndoorData = json.load(file, object_hook=IndoorData.jsonDecoder)
            
        ent: IndoorSensor = IndoorSensor()
        ent.channel = data.channel
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
        ent.raw = j

        repo.insert(ent)
        
        self.assertIsNotNone(ent.id)
