from datetime import date, timedelta, datetime

from entity.AQISensor import AQISensor
from repository.AQISensorRepository import AQISensorRepository
from repository.BaseRepository import BaseRepository
from tests.repository.BaseRepositoryTest import BaseRespositoryTest


class AQISensorRepositoryTest(BaseRespositoryTest):

    def getRepo(self) -> BaseRepository:
        return AQISensorRepository()

    def test(self):
        
        repo: AQISensorRepository = self.getRepo()

        data: AQISensor = AQISensor()
        data.pm_1_0_conctrt_std = 0
        data.pm_2_5_conctrt_std = 0
        data.pm_10_conctrt_std = 0

        data.pm_1_0_conctrt_atmosph = 0
        data.pm_2_5_conctrt_atmosph = 0
        data.pm_10_conctrt_atmosph = 0
        
        data.read_time = datetime.now()
        
        print(str(data))
        
        repo.insert(data)
        
        self.assertIsNotNone(data.id)
        
        act = repo.findById(data.id)
        self.assertIsNotNone(act)
        self.assertEqual(data.id, act.id)
        self.assertEqual(data.read_time, act.read_time)

        act = repo.findLatest()
        self.assertIsNotNone(act)
        self.assertEqual(data.id, act.id)
        self.assertEqual(data.read_time, act.read_time)

        d =(datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

        l = repo.findGreaterThanReadTime(d)
        self.assertIsNotNone(l)
        self.assertTrue(len(l) > 0)

    def test_clean(self):
        repo: BaseRepository = self.getRepo()
        
        repo.execFile("sql/sample/aqi_sensor.sql")
        
        repo.clean()
        
    def test_backup(self):
        repo: BaseRepository = self.getRepo()        
        repo.exec(f'truncate {repo.entity.__table__}')

        repo.execFile("sql/sample/aqi_sensor.sql")

        from_date: date = date.today() - timedelta(days=1)
        to_date: date = date.today() - timedelta(days=-1)
        
        repo.backup(from_date, to_date, "test.sql")
        
        repo.exec(f'truncate {repo.entity.__table__}')

        repo.execFile("test.sql")
        