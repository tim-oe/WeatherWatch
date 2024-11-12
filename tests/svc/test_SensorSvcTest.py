from datetime import datetime, timedelta
from decimal import Decimal
import time
import unittest

from sensor.sdr.OutdoorData import OutdoorData
from tests.sensor.sdr.test_OutdoorDataTest import OutdoorDataTest
from entity.IndoorSensor import IndoorSensor
from entity.OutdoorSensor import OutdoorSensor
from repository.IndoorSensorRepository import IndoorSensorRepository
from repository.OutdoorSensorRepository import OutdoorSensorRepository

from svc.SensorSvc import SensorSvc

class SensorSvcTest(unittest.TestCase):

    def setup_method(self, test_method):
        self.svc: SensorSvc = SensorSvc()
        self.indoorRepo: IndoorSensorRepository = IndoorSensorRepository()
        self.outdoorRepo: OutdoorSensorRepository = OutdoorSensorRepository()

        self.indoorRepo.exec('truncate ' + IndoorSensor.__tablename__)
        self.outdoorRepo.exec('truncate ' + OutdoorSensor.__tablename__)

    def teardown_class(self):
        IndoorSensorRepository().exec('truncate ' + IndoorSensor.__tablename__)
        OutdoorSensorRepository().exec('truncate ' + OutdoorSensor.__tablename__)
        
    def test(self):
        self.svc.process()
        
        os: OutdoorSensor = self.outdoorRepo.top(1)
        
        self.assertEqual(1, len(os))
        self.assertIsNotNone(os[0].rain_delta_mm)
        self.assertEqual(2, len(self.indoorRepo.top(2)))
        
        time.sleep(1)
        
        self.svc.process()

        os: OutdoorSensor = self.outdoorRepo.findLatest()
        self.assertIsNotNone(os)
        self.assertIsNotNone(os.rain_delta_mm)

    def test_delta_first(self):
        
        od: OutdoorData = OutdoorDataTest.getSample()
        
        self.svc.handleOutdoor(od)
        
        os: OutdoorSensor = self.outdoorRepo.findLatest()
        
        self.assertEqual(Decimal(0.0), os.rain_delta_mm)

    def test_delta_next(self):
        
        od1: OutdoorData = OutdoorDataTest.getSample()
        od1.timeStamp = datetime.now() - timedelta(minutes=5)

        self.svc.handleOutdoor(od1)
        
        os1: OutdoorSensor = self.outdoorRepo.findLatest()
        
        self.assertEqual(Decimal(0.0), os1.rain_delta_mm)
        
        od2: OutdoorData = OutdoorDataTest.getSample()
        
        self.svc.handleOutdoor(od2)
        
        os2: OutdoorSensor = self.outdoorRepo.findLatest()
        
        self.assertEqual(Decimal(0.0), os2.rain_delta_mm)

    def test_delta_rain(self):
        
        od1: OutdoorData = OutdoorDataTest.getSample()
        od1.timeStamp = datetime.now() - timedelta(minutes=5)
        
        od1.rain_mm = Decimal(0.0)
        
        self.svc.handleOutdoor(od1)
        
        os1: OutdoorSensor = self.outdoorRepo.findLatest()
        
        self.assertEqual(Decimal(0.0), os1.rain_delta_mm)
        
        od2: OutdoorData = OutdoorDataTest.getSample()
        od2.rain_mm = Decimal(1.1) 
        
        self.svc.handleOutdoor(od2)
        
        os2: OutdoorSensor = self.outdoorRepo.findLatest()
        
        self.assertEqual(Decimal('1.10'), os2.rain_delta_mm)

    def test_delta_reset(self):
        
        od1: OutdoorData = OutdoorDataTest.getSample()
        od1.timeStamp = datetime.now() - timedelta(minutes=5)
        
        od1.rain_mm = Decimal(2.0)
        
        self.svc.handleOutdoor(od1)
        
        os1: OutdoorSensor = self.outdoorRepo.findLatest()
        
        self.assertEqual(Decimal(0.0), os1.rain_delta_mm)
        
        od2: OutdoorData = OutdoorDataTest.getSample()
        od2.rain_mm = Decimal(1.1) 
        
        self.svc.handleOutdoor(od2)
        
        os2: OutdoorSensor = self.outdoorRepo.findLatest()
        
        self.assertEqual(Decimal('1.10'), os2.rain_delta_mm)
