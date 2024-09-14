import unittest

from src.sensor.sdr.SensorReader import SensorReader
from src.conf.AppConfig import AppConfig

ac = AppConfig()

class SensorReaderTest(unittest.TestCase):
    def test(self):
        bs: SensorReader = SensorReader()
        bs.read()