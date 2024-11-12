from datetime import date, datetime, timedelta

from decimal import Decimal

from repository.BaseRepository import BaseRepository
from tests.repository.BaseRepositoryTest import BaseRespositoryTest
from tests.sensor.sdr.test_OutdoorDataTest import OutdoorDataTest
from repository.OutdoorSensorRepository import OutdoorSensorRepository
from entity.OutdoorSensor import OutdoorSensor
from sensor.sdr.OutdoorData import OutdoorData

class OutdoorSensorRepositoryTest(BaseRespositoryTest):

    def getRepo(self) -> BaseRepository:
        return OutdoorSensorRepository()

    def test(self):
        
        repo: OutdoorSensorRepository = self.getRepo()
            
        ent: OutdoorSensor = OutdoorSensorRepositoryTest.getSample()

        repo.insert(ent)
        
        self.assertIsNotNone(ent.id)

        act = repo.findById(ent.id)
        self.assertIsNotNone(act)
        self.assertEqual(ent.id, act.id)
        self.assertEqual(ent.read_time, act.read_time)

        act = repo.findLatest()
        self.assertIsNotNone(act)
        self.assertEqual(ent.id, act.id)
        self.assertEqual(ent.read_time, act.read_time)
        
        d =(datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

        l = repo.findGreaterThanReadTime(d)
        self.assertIsNotNone(act)
        self.assertTrue(len(l) > 0)
        
        x = repo.getDaysRainfall(date.today())
        
        self.assertIsNotNone(x)
        self.assertIsInstance(x, Decimal)

    def test_sample(self):
        repo: BaseRepository = self.getRepo()        
        repo.execFile("sql/sample/outdoor_sensor.sql")

    @staticmethod
    def getSample() -> OutdoorSensor:
            
        data: OutdoorData = OutdoorDataTest.getSample()
            
        ent: OutdoorSensor = OutdoorSensor()
        ent.sensor_id = data.id
        ent.battery_ok = data.batteryOk
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
      
        