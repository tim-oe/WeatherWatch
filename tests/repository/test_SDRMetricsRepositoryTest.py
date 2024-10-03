import datetime
import unittest

from weatherwatch.entity.SDRMetricts import SDRMetrics
from weatherwatch.repository.SDRMetricsRepository import SDRMetricsRepository


class SDRMetrictsRepositoryTest(unittest.TestCase):

    def test(self):
        
        repo: SDRMetricsRepository = SDRMetricsRepository()

        ent: SDRMetrics = SDRMetrics()
        ent.start_time = datetime.datetime.now()
        ent.end_time = datetime.datetime.now()
        ent.duration_sec = 1
        ent.sensor_cnt = 1
        
        repo.insert(ent)
        
        self.assertIsNotNone(ent.id)
        act = repo.findById(ent.id)
        self.assertIsNotNone(act)
        # TODO not working...
        #self.assertEquals(ent, act)
        
