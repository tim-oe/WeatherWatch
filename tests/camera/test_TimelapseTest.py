from datetime import date
from pathlib import Path
import unittest

from camera.Timelapse import Timelapse
from weatherwatch.conf.AppConfig import AppConfig

class CameraTest(unittest.TestCase):

    def test(self):
        ac: AppConfig = AppConfig()
        
        tl: Timelapse = Timelapse()

        vid: Path = tl.process(date(2024,10,20),
            Path("tests/data/img"),
            Path("vid"))
        
        self.assertIsNotNone(vid)
        print(vid)        
