from datetime import date
from pathlib import Path
import unittest

from camera.Timelapse import Timelapse
from weatherwatch.conf.AppConfig import AppConfig

class CameraTest(unittest.TestCase):

    def test(self):        
        tl: Timelapse = Timelapse()

        vid: Path = tl.process(date(2024,10,20),
            Path("tests/data/img"),
            Path("vid"))
        
        self.assertIsNotNone(vid)
        print(vid)        

    # def test2(self):
        
    #     tl: Timelapse = Timelapse()
        
    #     for d in range(30, 31):
    #         vid: Path = tl.process(date(2024,10,d),
    #             Path("/mnt/clones/data/pix"),
    #             Path("/mnt/clones/data/vid"))
        
    #         self.assertIsNotNone(vid)
    #         print(vid)        
