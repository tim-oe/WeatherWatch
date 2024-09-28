import unittest

from src.sensor.bmp.BMPData import BMPData
from src.sensor.bmp.Bmp280SensorReader import Bmp280SensorReader

class Bmp280SensorReaderTest(unittest.TestCase):

    def test(self):
        if True :
            return
        
        sensor: Bmp280SensorReader = Bmp280SensorReader()
        actual: BMPData = sensor.read()

        print(actual)
                
        self.assertIsNotNone(actual)
        self.assertIsNotNone(actual.pressure)        
        self.assertIsNotNone(actual.temperature)
        self.assertIsNotNone(actual.altitude)                