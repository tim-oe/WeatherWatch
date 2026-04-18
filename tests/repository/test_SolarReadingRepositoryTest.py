from datetime import date, timedelta, datetime

from entity.SolarReading import SolarReading
from repository.BaseRepository import BaseRepository
from repository.SolarReadingRepository import SolarReadingRepository
from tests.repository.BaseRepositoryTest import BaseRespositoryTest


class SolarReadingRepositoryTest(BaseRespositoryTest):

    def getRepo(self) -> BaseRepository:
        return SolarReadingRepository()

    def test(self):

        repo: SolarReadingRepository = self.getRepo()

        ent: SolarReading = SolarReadingRepositoryTest.getSample()

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

        ent: SolarReading = SolarReadingRepositoryTest.getSample()
        repo.insert(ent)

        from_date: date = date.today() - timedelta(days=1)
        to_date: date = date.today() - timedelta(days=-1)

        repo.backup(from_date, to_date, "test.sql")

        repo.exec(f'truncate {repo.entity.__table__}')

        repo.exec_file("test.sql")

    @staticmethod
    def getSample() -> SolarReading:

        ent: SolarReading = SolarReading()
        ent.type = "solar"
        ent.name = "solar"
        ent.read_time = datetime.now()
        ent.read_duration_ms = 150.25

        ent.model = "RNG-CTRL-WND10"
        ent.device_id = 1

        ent.battery_percentage = 85
        ent.battery_voltage = 13.2
        ent.battery_current = 1.50
        ent.battery_temperature = 25
        ent.battery_type = "lithium"

        ent.controller_temperature = 30
        ent.charging_status = "mppt"

        ent.load_status = "on"
        ent.load_voltage = 12.1
        ent.load_current = 0.80
        ent.load_power = 10

        ent.pv_voltage = 18.5
        ent.pv_current = 2.10
        ent.pv_power = 38

        ent.battery_min_voltage_today = 12.0
        ent.battery_max_voltage_today = 14.4
        ent.max_charging_current_today = 3.50
        ent.max_discharging_current_today = 1.20
        ent.max_charging_power_today = 50
        ent.max_discharging_power_today = 15
        ent.charging_amp_hours_today = 12
        ent.discharging_amp_hours_today = 8
        ent.power_generation_today = 600.5
        ent.power_consumption_today = 200.3

        ent.power_generation_total = 150000

        return ent
