import unittest

import pprint

from conf.AppConfig import AppConfig
from conf.MqttConfig import MqttConfig


class MqttConfigTest(unittest.TestCase):
    def test(self):

        ac: AppConfig = AppConfig()
        mc: MqttConfig = ac.mqtt

        print(ac.mqtt)
        pprint.pprint(ac.mqtt.__dict__)

        self.assertTrue(mc.enable)
        self.assertIsNotNone(mc.host)
        self.assertIsNotNone(mc.port)
        self.assertIsNotNone(mc.solar_topic)
        self.assertIsNotNone(mc.temperature_topic)
        self.assertEqual(1883, mc.port)
        self.assertEqual("weatherwatch/solar", mc.solar_topic)
        self.assertEqual("weatherwatch/temperature", mc.temperature_topic)
