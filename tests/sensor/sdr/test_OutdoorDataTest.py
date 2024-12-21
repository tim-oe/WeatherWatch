from datetime import datetime
import json

from sensor.sdr.IndoorData import IndoorData
from sensor.sdr.OutdoorData import OutdoorData
from tests.sensor.sdr.BaseTestData import BaseTestData

class OutdoorDataTest(BaseTestData):

    def test(self):
        with open("tests/data/outdoor.json", "r") as file:
            expected = json.load(file)

        with open("tests/data/outdoor.json", "r") as file:
            record: OutdoorData = json.load(file, object_hook=OutdoorData.json_decoder)

        self.assertBase(expected, record)
        self.assertEqual(expected[IndoorData.HUMID_KEY], record.humidity)
        self.assertEqual(expected[IndoorData.TEMP_KEY], record.temperature)
        self.assertEqual(expected[OutdoorData.RAIN_KEY], record.rain_mm)
        self.assertEqual(expected[OutdoorData.WIND_AVE_KEY], record.wind_avg_m_s)
        self.assertEqual(expected[OutdoorData.WIND_MAX_KEY], record.wind_max_m_s)
        self.assertEqual(expected[OutdoorData.WIND_DIR_KEY], record.wind_dir_deg)
        self.assertEqual(expected[OutdoorData.LUX_KEY], record.light_lux)
        self.assertEqual(expected[OutdoorData.UV_KEY], record.uv)

    @staticmethod
    def getSample() -> OutdoorData:
        with open("tests/data/outdoor.json", "r") as file:
            j = json.load(file)

        with open("tests/data/outdoor.json", "r") as file:
            data: OutdoorData = json.load(file, object_hook=OutdoorData.json_decoder)
            
        data.time_stamp = datetime.now()
        data.raw = j
        
        return data
