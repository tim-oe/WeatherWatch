import unittest

from src.sensor.sdr.SensorReader import SensorReader


class SensorReaderTest(unittest.TestCase):
    def test(self):
        bs: SensorReader = SensorReader()

        bs.read()

        self.assertTrue(len(bs.reads) > 0)
