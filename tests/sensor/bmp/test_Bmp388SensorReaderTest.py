import unittest

import pytest

from sensor.bmp.BMPData import BMPData
from sensor.bmp.Bmp388SensorReader import Bmp388SensorReader


@pytest.mark.integration
class Bmp388SensorReaderTest(unittest.TestCase):
    """
    Integration tests for Bmp388SensorReader against the live BMP388 sensor.

    Requires a physical BMP388/BMP390 connected via I2C (board.SCL / board.SDA).
    Run with:  poetry run pytest -m integration tests/sensor/bmp/test_Bmp388SensorReaderTest.py
    """

    def test_read_returns_data(self):
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
