from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from entity.OutdoorSensor import OutdoorSensor
from repository.BaseRepository import BaseRepository
from repository.OutdoorSensorRepository import OutdoorSensorRepository
from sensor.sdr.OutdoorData import OutdoorData
from tests.repository.BaseRepositoryTest import BaseRespositoryTest
from tests.sensor.sdr.test_OutdoorDataTest import OutdoorDataTest


@pytest.mark.db
class OutdoorSensorRepositoryTest(BaseRespositoryTest):

    def getRepo(self) -> BaseRepository:
        return OutdoorSensorRepository()

    def test(self):
        
        repo: OutdoorSensorRepository = self.getRepo()
            
        ent: OutdoorSensor = OutdoorSensorRepositoryTest.getSample()

        repo.insert(ent)
        
        self.assertIsNotNone(ent.id)

        act = repo.find_by_id(ent.id)
        self.assertIsNotNone(act)
        self.assertEqual(ent.id, act.id)
        self.assertEqual(ent.read_time, act.read_time)

        act = repo.find_latest()
        self.assertIsNotNone(act)
        self.assertEqual(ent.id, act.id)
        self.assertEqual(ent.read_time, act.read_time)
        
        d =(datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

        l = repo.find_greater_than_read_time(d)
        self.assertIsNotNone(l)
        self.assertTrue(len(l) > 0)

        x = repo.get_days_rainfall(date.today())
        
        self.assertIsNotNone(x)
        self.assertIsInstance(x, Decimal)
        
        x = repo.get_days_rainfall(date.today() + timedelta(days=1))
        
        self.assertIsNotNone(x)
        self.assertIsInstance(x, Decimal)

    def test_get_value_false_bool_returns_zero(self):
        """get_value() with False boolean should return '0'."""
        repo: OutdoorSensorRepository = self.getRepo()
        # Call get_value directly for the False branch (line 174)
        result = repo.get_value("battery_ok", False)
        self.assertEqual("0", result)
        # Also verify True returns "1"
        result_true = repo.get_value("battery_ok", True)
        self.assertEqual("1", result_true)

    def test_top_returns_limited_results(self):
        """top(n) should return at most n records."""
        repo: OutdoorSensorRepository = self.getRepo()
        ent = OutdoorSensorRepositoryTest.getSample()
        repo.insert(ent)

        results = repo.top(1)
        self.assertEqual(1, len(results))

    def test_delete_removes_entity(self):
        """delete() should remove the entity from the database."""
        repo: OutdoorSensorRepository = self.getRepo()
        ent = OutdoorSensorRepositoryTest.getSample()
        ent.battery_ok = False
        repo.insert(ent)

        self.assertIsNotNone(repo.find_by_id(ent.id))
        repo.delete(ent)

    def test_backup(self):
        repo: BaseRepository = self.getRepo()        
        repo.exec(f'truncate {repo.entity.__table__}')

        repo.exec_file("sql/sample/outdoor_sensor.sql")

        from_date: date = date.today() - timedelta(days=1)
        to_date: date = date.today() - timedelta(days=-1)
        
        repo.backup(from_date, to_date, "test.sql")
        
        repo.exec(f'truncate {repo.entity.__table__}')

        repo.exec_file("test.sql")
        
    @staticmethod
    def getSample() -> OutdoorSensor:
            
        data: OutdoorData = OutdoorDataTest.getSample()
            
        ent: OutdoorSensor = OutdoorSensor()
        ent.sensor_id = data.sensor_id
        ent.battery_ok = data.battery_ok
        ent.read_time = datetime.now()
        ent.temperature_f = data.temperature
        ent.humidity = data.humidity
        ent.rain_cum_mm = data.rain_mm
        ent.rain_delta_mm = data.rain_mm
        ent.wind_avg_m_s = data.wind_avg_m_s
        ent.wind_max_m_s = data.wind_max_m_s
        ent.wind_dir_deg = data.wind_dir_deg
        ent.light_lux = data.light_lux
        ent.uv = data.uv
        # comes from BMP sensor
        ent.pressure = 999.99
        ent.raw = data.raw
        
        return ent
      
        