from pathlib import Path
import time
import unittest

from camera.Camera import Camera
from weatherwatch.conf.AppConfig import AppConfig
from weatherwatch.conf.CameraConfig import CameraConfig

class CameraTest(unittest.TestCase):

    # def test(self):
    #     ac: AppConfig = AppConfig()
    #     cc: CameraConfig = ac.camera
        
    #     c: Camera = Camera()
        
    #     for f in cc.folder.iterdir():
    #         f.unlink()

    #     c.process() 
        
    #     found: bool = False
        
    #     for file in cc.folder.glob(f"*{cc.extension}"):       
    #         found = True
        
    #     self.assertTrue(found)

    #     my_file = Path(cc.currentFile)
    #     self.assertTrue(my_file.is_file())

    #     for f in cc.folder.iterdir():
    #         f.unlink()

    #     c.processNight(1) 
        
    #     found = False
        
    #     for file in cc.folder.glob(f"*{cc.extension}"):       
    #         found = True
        
    #     self.assertTrue(found)

    #     my_file = Path(cc.currentFile)
    #     self.assertTrue(my_file.is_file())

    def testExposure(self):
        ac: AppConfig = AppConfig()
        cc: CameraConfig = ac.camera
        
        c: Camera = Camera()
        
        c.process() 

        for d in range(1, 4):
            time.sleep(1)                    
            c.processNight(d) 
        
        for d in range(1, 5):
            time.sleep(1)                    
            c.processNight(d * 5) 
 
