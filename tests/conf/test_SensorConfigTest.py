import unittest

from src.conf.AppConfig import AppConfig
from src.conf.SensorConfig import SensorConfig
from src.sensor.sdr.BaseData import BaseData
from src.sensor.sdr.IndoorData import IndoorData


class SensorConfigTest(unittest.TestCase):
    def test(self):

        ac = AppConfig()

        for expected in ac.conf[AppConfig.SDR_KEY][AppConfig.SENSORS_KEY]:
            sc: SensorConfig = SensorConfig(expected)
            self.assertEqual(expected[BaseData.MODEL_KEY], sc.model)
            self.assertEqual(expected[BaseData.ID_KEY], sc.id)
            self.assertEqual(expected[SensorConfig.NAME_KEY], sc.name)
            self.assertEqual(expected[SensorConfig.CLASS_KEY], sc.dataClass)
            self.assertEqual(expected[SensorConfig.DEVICE_KEY], sc.device)
            if IndoorData.CHANNEL_KEY in expected:
                self.assertEqual(expected[IndoorData.CHANNEL_KEY], sc.channel)
