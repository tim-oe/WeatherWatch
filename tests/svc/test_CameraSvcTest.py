from pathlib import Path
import unittest

from conf.AppConfig import AppConfig
from conf.CameraConfig import CameraConfig
from svc.CameraSvc import CameraSvc
from weatherwatch.entity.OutdoorSensor import OutdoorSensor
from weatherwatch.repository.OutdoorSensorRepository import OutdoorSensorRepository

class SensorSvcTest(unittest.TestCase):
    
    def test(self):
        svc: CameraSvc = CameraSvc()
        ac: AppConfig = AppConfig()
        cc: CameraConfig = ac.camera
        
        outdoorRepo: OutdoorSensorRepository = OutdoorSensorRepository()

        outdoorRepo.exec('truncate ' + OutdoorSensor.__tablename__)
        outdoorRepo.execFile("sql/sample/outdoor_sensor.sql")
        
        for f in cc.folder.iterdir():
            f.unlink()

        svc.process()
        
        found: bool = False
        
        for file in cc.folder.glob(f"*{cc.extension}"):       
            found = True
        
        self.assertTrue(found)

        my_file = Path(cc.currentFile)
        self.assertTrue(my_file.is_file())
        