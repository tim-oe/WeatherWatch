import unittest

import pprint

from conf.AppConfig import AppConfig
from conf.AQIConfig import AQIConfig

class AQIConfigTest(unittest.TestCase):
    def test(self):

        ac: AppConfig = AppConfig()
        sc: AQIConfig = ac.aqi
        
        print(ac.aqi)
        pprint.pprint(ac.aqi.__dict__)
        
        self.assertTrue(sc.enable)
 