import unittest
from unittest.mock import MagicMock, PropertyMock, patch

from sensor.bmp.BMPData import BMPData
from sensor.bmp.Bmp388SensorReader import Bmp388SensorReader


class Bmp388SensorReaderMockTest(unittest.TestCase):
    """
    Unit tests for Bmp388SensorReader with all I2C hardware mocked out.

    board.I2C() and adafruit_bmp3xx.BMP3XX_I2C() are patched so no physical
    sensor or Pi GPIO is required.  The singleton is reset before and after
    every test to ensure isolation.
    """

    def setUp(self):
        Bmp388SensorReader.inst = None
        Bmp388SensorReader.inited = False

        self._patcher_board = patch("sensor.bmp.Bmp388SensorReader.board")
        self._patcher_bmp_mod = patch("sensor.bmp.Bmp388SensorReader.adafruit_bmp3xx")

        self._patcher_board.start()
        mock_bmp_mod = self._patcher_bmp_mod.start()

        self._mock_bmp = MagicMock()
        type(self._mock_bmp).pressure = PropertyMock(return_value=1013.25)
        type(self._mock_bmp).temperature = PropertyMock(return_value=22.5)
        type(self._mock_bmp).altitude = PropertyMock(return_value=50.0)
        mock_bmp_mod.BMP3XX_I2C.return_value = self._mock_bmp

        self._sensor = Bmp388SensorReader()

    def tearDown(self):
        self._patcher_board.stop()
        self._patcher_bmp_mod.stop()
        Bmp388SensorReader.inst = None
        Bmp388SensorReader.inited = False

    # ------------------------------------------------------------------
    # __init__ configuration
    # ------------------------------------------------------------------

    def test_pressure_oversampling_set_on_init(self):
        """pressure_oversampling is configured to 8 during init."""
        self.assertEqual(8, self._mock_bmp.pressure_oversampling)

    def test_temperature_oversampling_set_on_init(self):
        """temperature_oversampling is configured to 2 during init."""
        self.assertEqual(2, self._mock_bmp.temperature_oversampling)

    # ------------------------------------------------------------------
    # read()
    # ------------------------------------------------------------------

    def test_read_returns_bmpdata_instance(self):
        """read() returns a BMPData object."""
        data = self._sensor.read()
        self.assertIsInstance(data, BMPData)

    def test_read_populates_all_fields(self):
        """read() populates pressure, temperature, and altitude."""
        data = self._sensor.read()
        self.assertIsNotNone(data.pressure)
        self.assertIsNotNone(data.temperature)
        self.assertIsNotNone(data.altitude)

    def test_read_pressure_value(self):
        """read() maps bmp.pressure to BMPData.pressure."""
        data = self._sensor.read()
        self.assertEqual(1013.25, data.pressure)

    def test_read_temperature_value(self):
        """read() maps bmp.temperature to BMPData.temperature."""
        data = self._sensor.read()
        self.assertEqual(22.5, data.temperature)

    def test_read_altitude_value(self):
        """read() maps bmp.altitude to BMPData.altitude."""
        data = self._sensor.read()
        self.assertEqual(50.0, data.altitude)
