import datetime

import psutil
import pytest

from entity.PIMetrics import PIMetrics
from repository.BaseRepository import BaseRepository
from repository.PIMetricsRepository import PIMetricsRepository
from tests.repository.BaseRepositoryTest import BaseRespositoryTest


@pytest.mark.db
class PIMetricsRepositoryTest(BaseRespositoryTest):

    def getRepo(self) -> BaseRepository:
        return PIMetricsRepository()

    def test(self):
        
        repo: PIMetricsRepository = self.getRepo()

        data: PIMetrics = PIMetrics()
        data.read_time = datetime.datetime.now()
        
        mem = psutil.virtual_memory()        
        data.mem_available = mem.available
        data.mem_used = mem.used
        data.mem_percent = mem.percent

        disk = psutil.disk_usage("/")
        data.disk_available = disk.free
        data.disk_used = disk.used
        data.disk_percent = disk.percent

        temps = psutil.sensors_temperatures()
        zone = temps.get("cpu_thermal") or next(iter(temps.values()), None)
        data.cpu_temp_c = zone[0].current if zone else 0

        print(str(data))
        
        repo.insert(data)
        
        self.assertIsNotNone(data.id)
        
        act = repo.find_by_id(data.id)
        self.assertIsNotNone(act)
        self.assertEqual(data.id, act.id)
        self.assertEqual(data.read_time, act.read_time)
