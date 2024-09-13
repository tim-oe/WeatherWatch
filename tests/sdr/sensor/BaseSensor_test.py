import unittest

from src.sensor.sdr.BaseSensor import BaseSensor

class BaseSensorTest(unittest.TestCase):
    def test(self):
        bs: BaseSensor = BaseSensor()
        bs.read()