import unittest

import datetime

from entity.AQISensor import AQISensor
from repository.AQISensorRepository import AQISensorRepository


class AQISensorRepositoryTest(unittest.TestCase):

    def test(self):
        
        repo: AQISensorRepository = AQISensorRepository()

        data: AQISensor = AQISensor()
        data.pm_1_0_conctrt_std = 0
        data.pm_2_5_conctrt_std = 0
        data.pm_10_conctrt_std = 0

        data.pm_1_0_conctrt_atmosph = 0
        data.pm_2_5_conctrt_atmosph = 0
        data.pm_10_conctrt_atmosph = 0
        
        data.read_time = datetime.datetime.now()
        
        print(str(data))
        
        repo.insert(data)
        
        self.assertIsNotNone(data.id)
        
        act = repo.findById(data.id)
        self.assertIsNotNone(act)
        self.assertEqual(data.id, act.id)
        self.assertEqual(data.read_time, act.read_time)