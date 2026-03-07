from datetime import date, timedelta, datetime

from entity.LightSensor import LightSensor
from repository.BaseRepository import BaseRepository
from repository.LightSensorRepository import LightSensorRepository
from tests.repository.BaseRepositoryTest import BaseRespositoryTest


class LightSensorRepositoryTest(BaseRespositoryTest):

    def getRepo(self) -> BaseRepository:
        return LightSensorRepository()

    def test(self):
        
        repo: LightSensorRepository = self.getRepo()

        ent: LightSensor = LightSensorRepositoryTest.getSample()
        
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

    def test_backup(self):
        repo: BaseRepository = self.getRepo()        
        repo.exec(f'truncate {repo.entity.__table__}')

        ent: LightSensor = LightSensorRepositoryTest.getSample()
        repo.insert(ent)

        from_date: date = date.today() - timedelta(days=1)
        to_date: date = date.today() - timedelta(days=-1)
        
        repo.backup(from_date, to_date, "test.sql")
        
        repo.exec(f'truncate {repo.entity.__table__}')

        repo.exec_file("test.sql")

    @staticmethod
    def getSample() -> LightSensor:

        ent: LightSensor = LightSensor()
        ent.read_time = datetime.now()
        ent.lux = 250.75
        ent.visible = 3200
        ent.infrared = 850
        ent.full_spectrum = 4050
        ent.ir_visible_luminosity = 4050
        ent.ir_only = 850

        return ent
