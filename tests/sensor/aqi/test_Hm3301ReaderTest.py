import unittest

import pytest

from sensor.aqi.Hm3301Data import Hm3301Data
from sensor.aqi.Hm3301Reader import Hm3301Reader


@pytest.mark.integration
class Hm3301ReaderTest(unittest.TestCase):
    """
    Integration tests for Hm3301Reader against the live HM3301 sensor.

    Requires a physical HM3301 connected via I2C at bus 1, address 0x40.
    I2C bus speed must be set to 20 kHz (dtparam=i2c_arm_baudrate=20000).
    Run with:  poetry run pytest -m integration tests/sensor/aqi/test_Hm3301ReaderTest.py
    """

    def test_read_returns_data(self):
        reader = Hm3301Reader()
        data: Hm3301Data = reader.read()

        self.assertIsNotNone(data)
        self.assertGreaterEqual(data.pm_1_0_conctrt_std, 0)
        self.assertGreaterEqual(data.pm_2_5_conctrt_std, 0)
        self.assertGreaterEqual(data.pm_10_conctrt_std, 0)
        self.assertGreaterEqual(data.pm_1_0_conctrt_atmosph, 0)
        self.assertGreaterEqual(data.pm_2_5_conctrt_atmosph, 0)
        self.assertGreaterEqual(data.pm_10_conctrt_atmosph, 0)
