import unittest

import pytest

from sensor.light.Tsl2591SensorReader import Tsl2591SensorReader


@pytest.mark.integration
class Tsl2591SensorReaderTest(unittest.TestCase):
    """
    Integration tests for Tsl2591SensorReader against the live TSL2591 sensor.

    Requires a physical TSL2591 connected via I2C (board.SCL / board.SDA).
    Run with:  poetry run pytest -m integration tests/sensor/light/test_Tsl2591SensorReaderTest.py
    """

    def test_read_returns_data(self):
        sensor = Tsl2591SensorReader()
        data = sensor.read()
        self.assertIsNotNone(data)

    def test_get_lux_returns_positive_value(self):
        sensor = Tsl2591SensorReader()
        lux = sensor.get_lux()
        self.assertGreater(lux, 0)
