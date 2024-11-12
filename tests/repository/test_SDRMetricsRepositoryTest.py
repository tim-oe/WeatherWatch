import datetime
import unittest

from repository.BaseRepository import BaseRepository
from tests.repository.BaseRepositoryTest import BaseRespositoryTest
from entity.SDRMetricts import SDRMetrics
from repository.SDRMetricsRepository import SDRMetricsRepository

class SDRMetrictsRepositoryTest(BaseRespositoryTest):

    def getRepo(self) -> BaseRepository:
        return SDRMetricsRepository()

    def test(self):
        
        repo: SDRMetricsRepository = self.getRepo()

        ent: SDRMetrics = SDRMetrics()
        ent.start_time = datetime.datetime.now()
        ent.end_time = datetime.datetime.now()
        ent.duration_sec = 1
        ent.sensor_cnt = 1
        
        repo.insert(ent)
        print(str(ent))
        
        self.assertIsNotNone(ent.id)
        
        act = repo.findById(ent.id)
        self.assertIsNotNone(act)
        self.assertEqual(ent.id, act.id)
        self.assertEqual(ent.start_time, act.start_time)
        self.assertEqual(ent.end_time, act.end_time)
        self.assertEqual(ent.duration_sec, act.duration_sec)
        self.assertEqual(ent.sensor_cnt, act.sensor_cnt)
