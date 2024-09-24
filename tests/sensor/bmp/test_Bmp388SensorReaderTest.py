import unittest

from src.sensor.bmp.SensorData import SensorData
from src.sensor.bmp.Bmp388SensorReader import Bmp388SensorReader

class Bmp388SensorReaderTest(unittest.TestCase):

    def test(self):
        sensor: Bmp388SensorReader = Bmp388SensorReader()
        actual: SensorData = sensor.read()

        print(actual)
                
        self.assertIsNotNone(actual)
        self.assertIsNotNone(actual.pressure)        
        self.assertIsNotNone(actual.temperature)
        self.assertIsNotNone(actual.altitude)                