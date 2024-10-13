import unittest

from weatherwatch.conf.AppConfig import AppConfig
from weatherwatch.conf.CameraConfig import CameraConfig

class CameraConfigTest(unittest.TestCase):
    def test(self):

        ac: AppConfig = AppConfig()
        sc: CameraConfig = ac.camera
        
        self.assertTrue(sc.enable)
        self.assertIsNotNone(sc.folder)
 