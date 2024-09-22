import unittest

from src.sensor.bmp388.SensorData import SensorData
from src.sensor.bmp388.SensorReader import SensorReader

class SensorReaderTest(unittest.TestCase):

    def test(self):
        sensor: SensorReader = SensorReader()
        actual: SensorData = sensor.read()

        print(actual)
                
        self.assertIsNotNone(actual)
        self.assertIsNotNone(actual.pressure)        
        self.assertIsNotNone(actual.temperature)
        self.assertIsNotNone(actual.altitude)                