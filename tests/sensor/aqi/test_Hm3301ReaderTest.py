import unittest

from weatherwatch.sensor.aqi.Hm3301Data import Hm3301Data
from weatherwatch.sensor.aqi.Hm3301Reader import Hm3301Reader

class Hm3301ReaderTest(unittest.TestCase):
    def test(self):
        bs: Hm3301Reader = Hm3301Reader()
        
        data: Hm3301Data = bs.read()

        self.assertIsNotNone(data)

        self.assertTrue(data.pm_1_0_conctrt_std > 0)
        self.assertTrue(data.pm_2_5_conctrt_std > 0)
        self.assertTrue(data.pm_10_conctrt_std > 0)
        self.assertTrue(data.pm_1_0_conctrt_atmosph > 0)
        self.assertTrue(data.pm_2_5_conctrt_atmosph > 0)
        self.assertTrue(data.pm_10_conctrt_atmosph > 0)

