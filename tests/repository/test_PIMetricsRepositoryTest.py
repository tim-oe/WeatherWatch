import datetime

import psutil

from repository.BaseRepository import BaseRepository
from tests.repository.BaseRepositoryTest import BaseRespositoryTest
from repository.PIMetricsRepository import PIMetricsRepository
from entity.PIMetrics import PIMetrics


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

        cpu = psutil.sensors_temperatures()
        data.cpu_temp_c = cpu['cpu_thermal'][0].current

        print(str(data))
        
        repo.insert(data)
        
        self.assertIsNotNone(data.id)
        
        act = repo.find_by_id(data.id)
        self.assertIsNotNone(act)
        self.assertEqual(data.id, act.id)
        self.assertEqual(data.read_time, act.read_time)
