import unittest

import pprint

from conf.DashConfig import DashConfig
from conf.AppConfig import AppConfig
from conf.AQIConfig import AQIConfig

class DashboardConfigTest(unittest.TestCase):
    def test(self):

        ac: AppConfig = AppConfig()
        sc: DashConfig = ac.dashboard
    
        print(ac.dashboard)
        pprint.pprint(ac.dashboard.__dict__)

        self.assertIsNotNone(sc.host)
        
        self.assertGreater(sc.port, 0)
        
        self.assertFalse(sc.debug)
 