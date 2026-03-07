import unittest

from sensor.light.Tsl2591SensorReader import Tsl2591SensorReader

class Tsl2591SensorReaderTest(unittest.TestCase):

    def test(self):
        sensor: Tsl2591SensorReader = Tsl2591SensorReader()
        print(sensor.read())
        print(sensor.get_lux())