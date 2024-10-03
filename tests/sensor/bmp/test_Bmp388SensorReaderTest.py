import unittest

from weatherwatch.sensor.bmp.BMPData import BMPData
from weatherwatch.sensor.bmp.Bmp388SensorReader import Bmp388SensorReader

class Bmp388SensorReaderTest(unittest.TestCase):

    def test(self):
        sensor: Bmp388SensorReader = Bmp388SensorReader()
        actual: BMPData = sensor.read()

        print(actual)
                
        self.assertIsNotNone(actual)
        self.assertIsNotNone(actual.pressure)        
        self.assertIsNotNone(actual.temperature)
        self.assertIsNotNone(actual.altitude)                