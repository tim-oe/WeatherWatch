from datetime import date, timedelta, datetime

from entity.TemperatureReading import TemperatureReading
from repository.BaseRepository import BaseRepository
from repository.TemperatureReadingRepository import TemperatureReadingRepository
from tests.repository.BaseRepositoryTest import BaseRespositoryTest


class TemperatureReadingRepositoryTest(BaseRespositoryTest):

    def getRepo(self) -> BaseRepository:
        return TemperatureReadingRepository()

    def test(self):

        repo: TemperatureReadingRepository = self.getRepo()

        ent: TemperatureReading = TemperatureReadingRepositoryTest.getSample()

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

        d = (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

        l = repo.find_greater_than_read_time(d)
        self.assertIsNotNone(l)
        self.assertTrue(len(l) > 0)

    def test_backup(self):
        repo: BaseRepository = self.getRepo()
        repo.exec(f'truncate {repo.entity.__table__}')

        ent: TemperatureReading = TemperatureReadingRepositoryTest.getSample()
        repo.insert(ent)

        from_date: date = date.today() - timedelta(days=1)
        to_date: date = date.today() - timedelta(days=-1)

        repo.backup(from_date, to_date, "test.sql")

        repo.exec(f'truncate {repo.entity.__table__}')

        repo.exec_file("test.sql")

    @staticmethod
    def getSample() -> TemperatureReading:

        ent: TemperatureReading = TemperatureReading()
        ent.type = "temperature"
        ent.name = "battery_temp"
        ent.read_time = datetime.now()
        ent.read_duration_ms = 50.10

        ent.value = 22.375
        ent.unit = "C"

        return ent
