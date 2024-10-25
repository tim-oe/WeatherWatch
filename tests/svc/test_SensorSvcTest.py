import unittest

from weatherwatch.entity.IndoorSensor import IndoorSensor
from weatherwatch.entity.OutdoorSensor import OutdoorSensor
from weatherwatch.repository.IndoorSensorRepository import IndoorSensorRepository
from weatherwatch.repository.OutdoorSensorRepository import OutdoorSensorRepository

from weatherwatch.svc.SensorSvc import SensorSvc

class SensorSvcTest(unittest.TestCase):
    def test(self):
        svc: SensorSvc = SensorSvc()
        indoorRepo: IndoorSensorRepository = IndoorSensorRepository()
        outdoorRepo: OutdoorSensorRepository = OutdoorSensorRepository()

        indoorRepo.exec('truncate ' + IndoorSensor.__tablename__)
        indoorRepo.exec('truncate ' + OutdoorSensor.__tablename__)
        
        svc.process()
        
        os: OutdoorSensor = outdoorRepo.top(1)
        
        self.assertEqual(1, len(os))
        self.assertIsNotNone(os[0].rain_delta_mm)
        self.assertEqual(2, len(indoorRepo.top(2)))