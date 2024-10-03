import unittest

from weatherwatch.entity.IndoorSensor import IndoorSensor
from weatherwatch.entity.OutdoorSensor import OutdoorSensor
from weatherwatch.repository.IndoorSensorRepository import IndoorSensorRepository
from weatherwatch.repository.OutdoorSensorRepository import OutdoorSensorRepository

from weatherwatch.svc.SensorSvc import SensorSvc

# TODO need more thorough test to see if it actually read and inserted
class SensorSvcTest(unittest.TestCase):
    def test(self):
        svc: SensorSvc = SensorSvc()
        indoorRepo: IndoorSensorRepository = IndoorSensorRepository()
        outdoorRepo: OutdoorSensorRepository = OutdoorSensorRepository()

        indoorRepo.exec('truncate ' + IndoorSensor.__tablename__)
        indoorRepo.exec('truncate ' + OutdoorSensor.__tablename__)
        
        svc.process()
        
        self.assertEqual(1, len(outdoorRepo.top(1)))
        self.assertEqual(2, len(indoorRepo.top(2)))
        
