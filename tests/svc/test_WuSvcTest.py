
from datetime import datetime
import unittest
from unittest import mock
from urllib.parse import ParseResult

from entity.IndoorSensor import IndoorSensor
from entity.OutdoorSensor import OutdoorSensor
from repository.IndoorSensorRepository import IndoorSensorRepository
from repository.OutdoorSensorRepository import OutdoorSensorRepository
from svc.WUSvc import WUSvc
from wu.WUClient import WUClient
from wu.WUData import WUData

class WuSvcTest(unittest.TestCase):

    def post(self, readTime: datetime, data: WUData, endPoint: ParseResult = WUClient.END_POINT_URL):
        self._read_time = readTime
        self._data = data  

    def setup_method(self, test_method):
        self.svc: WUSvc = WUSvc()
        self._outdoorRepo: OutdoorSensorRepository = OutdoorSensorRepository()
        self.indoorRepo: IndoorSensorRepository = IndoorSensorRepository()

        self._outdoorRepo.exec('truncate ' + OutdoorSensor.__tablename__)
        self._outdoorRepo.exec_file("sql/sample/outdoor_sensor.sql")

        self.indoorRepo.exec('truncate ' + IndoorSensor.__tablename__)
        self.indoorRepo.exec_file("sql/sample/indoor_sensor.sql")

    def teardown_class(self):
        IndoorSensorRepository().exec('truncate ' + IndoorSensor.__tablename__)
        OutdoorSensorRepository().exec('truncate ' + OutdoorSensor.__tablename__)

    # mock posting to it not actually posts to WU
    #@mock.patch.object(WUClient, 'post', post)    
    def test(self):
        with mock.patch.object(WUClient, 'post', self.post):
            self.svc.process()
            
            self.assertIsNotNone(self._read_time)
            print(f"{self._read_time}")
            self.assertIsNotNone(self._data)
            print(f"{self._data}")
            
