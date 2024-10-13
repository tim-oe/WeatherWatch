import unittest

from camera.Camera import Camera
from weatherwatch.conf.AppConfig import AppConfig
from weatherwatch.conf.CameraConfig import CameraConfig

class CameraTest(unittest.TestCase):

    def test(self):
        ac: AppConfig = AppConfig()
        cc: CameraConfig = ac.camera
        
        c: Camera = Camera()
        
        for f in cc.folder.iterdir():
            f.unlink()

        c.process() 
        
        found: bool = False
        
        for file in cc.folder.glob(f"*{cc.extension}"):       
            found = True
        
        self.assertTrue(found)

        for f in cc.folder.iterdir():
            f.unlink()

        c.process() 
        
        found = False
        
        for file in cc.folder.glob(f"*{cc.extension}"):       
            found = True
        
        self.assertTrue(found)
