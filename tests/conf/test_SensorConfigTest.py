import unittest

import pprint

from conf.AppConfig import AppConfig
from conf.SensorConfig import SensorConfig
from sensor.sdr.BaseData import BaseData
from sensor.sdr.IndoorData import IndoorData

class SensorConfigTest(unittest.TestCase):
    def test(self):

        ac = AppConfig()

        pprint.pprint(ac.database)

        for expected in ac.conf[AppConfig.SDR_KEY][AppConfig.SENSORS_KEY]:
            pprint.pprint(expected)

            sc: SensorConfig = SensorConfig(expected)
            print(sc)

            self.assertEqual(expected[BaseData.MODEL_KEY], sc.model)
            self.assertEqual(expected[BaseData.ID_KEY], sc.id)
            self.assertEqual(expected[SensorConfig.NAME_KEY], sc.name)
            self.assertEqual(expected[SensorConfig.CLASS_KEY], sc.data_class)
            self.assertEqual(expected[SensorConfig.DEVICE_KEY], sc.device)
            if IndoorData.CHANNEL_KEY in expected:
                self.assertEqual(expected[IndoorData.CHANNEL_KEY], sc.channel)
