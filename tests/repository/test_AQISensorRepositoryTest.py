from datetime import timedelta, datetime

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

    def test_sample(self):
        repo: BaseRepository = self.getRepo()
        
        repo.execFile("sql/sample/aqi_sensor.sql")
        
        repo.clean()