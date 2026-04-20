import unittest

from sensor.bmp.BMPData import BMPData
from sensor.bmp.Bmp388SensorReader import Bmp388SensorReader


class Bmp388SensorReaderTest(unittest.TestCase):

    def test(self):
        sensor: Bmp388SensorReader = Bmp388SensorReader()
        actual: BMPData = sensor.read()

        print(actual)

        self.assertIsNotNone(actual)
        self.assertIsNotNone(actual.pressure)
        self.assertIsNotNone(actual.temperature)
        self.assertIsNotNone(actual.altitude)


class BMPDataTest(unittest.TestCase):
    """Unit tests for BMPData setters — no hardware required."""

    def test_temperature_setter(self):
        d = BMPData(temperature=25.0, pressure=1013.0, altitude=100.0)
        d.temperature = 30.0
        self.assertEqual(30.0, d.temperature)

    def test_pressure_setter(self):
        d = BMPData(temperature=25.0, pressure=1013.0, altitude=100.0)
        d.pressure = 1010.5
        self.assertEqual(1010.5, d.pressure)

    def test_altitude_setter(self):
        d = BMPData(temperature=25.0, pressure=1013.0, altitude=100.0)
        d.altitude = 200.0
        self.assertEqual(200.0, d.altitude)