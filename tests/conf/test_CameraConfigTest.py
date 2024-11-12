import unittest

import pprint

from conf.AppConfig import AppConfig
from conf.CameraConfig import CameraConfig

class CameraConfigTest(unittest.TestCase):
    def test(self):

        ac: AppConfig = AppConfig()
        sc: CameraConfig = ac.camera

        print(ac.camera)
        pprint.pprint(ac.camera.__dict__)
        
        self.assertTrue(sc.enable)
        self.assertIsNotNone(sc.folder)
 