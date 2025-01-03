import json

from sensor.sdr.IndoorData import IndoorData
from tests.sensor.sdr.BaseTestData import BaseTestData

class IndoorDataTest(BaseTestData):

    def test(self):
        with open("tests/data/indoor.json", "r") as file:
            expected = json.load(file)

        with open("tests/data/indoor.json", "r") as file:
            record: IndoorData = json.load(file, object_hook=IndoorData.json_decoder)

        self.assertBase(expected, record)
        self.assertEqual(expected[IndoorData.CHANNEL_KEY], record.channel)
        self.assertEqual(expected[IndoorData.HUMID_KEY], record.humidity)
        self.assertEqual(expected[IndoorData.TEMP_KEY], record.temperature)
