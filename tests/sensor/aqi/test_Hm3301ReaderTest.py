import unittest

from sensor.aqi.Hm3301Data import Hm3301Data
from sensor.aqi.Hm3301Reader import Hm3301Reader

class Hm3301ReaderTest(unittest.TestCase):
    def test(self):
        bs: Hm3301Reader = Hm3301Reader()
        
        data: Hm3301Data = bs.read()

        self.assertIsNotNone(data)

        self.assertTrue(data.pm_1_0_conctrt_std >= 0)
        self.assertTrue(data.pm_2_5_conctrt_std >= 0)
        self.assertTrue(data.pm_10_conctrt_std >= 0)
        self.assertTrue(data.pm_1_0_conctrt_atmosph >= 0)
        self.assertTrue(data.pm_2_5_conctrt_atmosph >= 0)
        self.assertTrue(data.pm_10_conctrt_atmosph >= 0)

    def testLower(self):
        d1: Hm3301Data = Hm3301Data()
        d1.pm_1_0_conctrt_std = 2
        d1.pm_2_5_conctrt_std = 3
        d1.pm_10_conctrt_std = 4
        d1.pm_1_0_conctrt_atmosph = 5
        d1.pm_2_5_conctrt_atmosph = 6
        d1.pm_10_conctrt_atmosph = 7

        d2: Hm3301Data = Hm3301Data()
        d2.pm_1_0_conctrt_std = 1
        d2.pm_2_5_conctrt_std = 2
        d2.pm_10_conctrt_std = 3
        d2.pm_1_0_conctrt_atmosph = 4
        d2.pm_2_5_conctrt_atmosph = 5
        d2.pm_10_conctrt_atmosph = 6

        d1.lower(d2, 0)
        
        self.assertEqual(d1.pm_1_0_conctrt_std, 1)
        self.assertEqual(d1.pm_2_5_conctrt_std, 2)
        self.assertEqual(d1.pm_10_conctrt_std, 3)
        self.assertEqual(d1.pm_1_0_conctrt_atmosph, 4)
        self.assertEqual(d1.pm_2_5_conctrt_atmosph, 5)
        self.assertEqual(d1.pm_10_conctrt_atmosph, 6)
        