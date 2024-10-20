import unittest

from weatherwatch.conf.AppConfig import AppConfig
from weatherwatch.conf.AQIConfig import AQIConfig

class AQIConfigTest(unittest.TestCase):
    def test(self):

        ac: AppConfig = AppConfig()
        sc: AQIConfig = ac.aqi
        
        self.assertTrue(sc.enable)
 