from datetime import date, datetime, timedelta

import json

from repository.BaseRepository import BaseRepository
from tests.repository.BaseRepositoryTest import BaseRespositoryTest
from repository.IndoorSensorRepository import IndoorSensorRepository
from entity.IndoorSensor import IndoorSensor
from sensor.sdr.IndoorData import IndoorData

class IndoorSensorRepositoryTest(BaseRespositoryTest):

    def getRepo(self) -> BaseRepository:
        return IndoorSensorRepository()

    def test(self):        
        repo: IndoorSensorRepository = self.getRepo()

        with open("tests/data/indoor.json", "r") as file:
            j = json.load(file)

        with open("tests/data/indoor.json", "r") as file:
            data: IndoorData = json.load(file, object_hook=IndoorData.jsonDecoder)
            
        ent: IndoorSensor = IndoorSensor()
        ent.channel = data.channel
        ent.temperature_f = data.temperature
        ent.humidity = data.humidity
        ent.sensor_id = data.id
        ent.battery_ok = data.batteryOk
        ent.read_time = datetime.now()
        ent.raw = j

        repo.insert(ent)
        
        print(str(ent))
        
        self.assertIsNotNone(ent.id)

        act = repo.findById(ent.id)
        self.assertIsNotNone(act)
        self.assertEqual(ent.id, act.id)
        self.assertEqual(ent.read_time, act.read_time)

        act = repo.findLatest(ent.channel)
        self.assertIsNotNone(act)
        self.assertEqual(ent.id, act.id)
        self.assertEqual(ent.read_time, act.read_time)

        d =(datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

        l = repo.findGreaterThanReadTime(ent.channel, d)
        self.assertIsNotNone(act)
        self.assertTrue(len(l) > 0)

    def test_backup(self):
        repo: BaseRepository = self.getRepo()        
        repo.exec(f'truncate {repo.entity.__table__}')

        repo.execFile("sql/sample/indoor_sensor.sql")

        from_date: date = date.today() - timedelta(days=1)
        to_date: date = date.today() - timedelta(days=-1)
        
        repo.backup(from_date, to_date, "test.sql")
        
        repo.exec(f'truncate {repo.entity.__table__}')

        repo.execFile("test.sql")
