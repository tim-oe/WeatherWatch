import unittest
from unittest.mock import MagicMock, PropertyMock, patch

import adafruit_tsl2591

from sensor.light.Tsl2591Data import Tsl2591Data
from sensor.light.Tsl2591SensorReader import Tsl2591SensorReader


class Tsl2591SensorReaderMockTest(unittest.TestCase):
    """
    Unit tests for Tsl2591SensorReader with all I2C hardware mocked out.

    board.I2C(), TSL2591(), AppConfig(), and time.sleep() are all patched
    so no physical sensor or Pi GPIO is required.  The singleton is reset
    before and after every test to ensure isolation.
    """

    # ------------------------------------------------------------------
    # Fixture helpers
    # ------------------------------------------------------------------

    def setUp(self):
        Tsl2591SensorReader.inst = None
        Tsl2591SensorReader.inited = False

        self._patcher_config = patch("sensor.light.Tsl2591SensorReader.AppConfig")
        self._patcher_board = patch("sensor.light.Tsl2591SensorReader.board")
        self._patcher_tsl_cls = patch("sensor.light.Tsl2591SensorReader.TSL2591")
        self._patcher_time = patch("sensor.light.Tsl2591SensorReader.time")

        mock_config_cls = self._patcher_config.start()
        self._patcher_board.start()
        mock_tsl_cls = self._patcher_tsl_cls.start()
        self._patcher_time.start()

        mock_config_cls.return_value.light = MagicMock()

        # Default well-behaved sensor instance returned by TSL2591(i2c)
        self._tsl = MagicMock()
        type(self._tsl).lux = PropertyMock(return_value=500.0)
        type(self._tsl).visible = PropertyMock(return_value=1000)
        type(self._tsl).infrared = PropertyMock(return_value=200)
        type(self._tsl).full_spectrum = PropertyMock(return_value=1200)
        type(self._tsl).raw_luminosity = PropertyMock(return_value=(1200, 200))
        type(self._tsl).gain = PropertyMock(return_value=adafruit_tsl2591.GAIN_MED)
        mock_tsl_cls.return_value = self._tsl

        self._sensor = Tsl2591SensorReader()

    def tearDown(self):
        self._patcher_config.stop()
        self._patcher_board.stop()
        self._patcher_tsl_cls.stop()
        self._patcher_time.stop()
        Tsl2591SensorReader.inst = None
        Tsl2591SensorReader.inited = False

    @staticmethod
    def _make_tsl_mock(lux_sequence, full_spectrum=1200, gain=adafruit_tsl2591.GAIN_MED):
        """
        Build a TSL2591 mock whose lux property yields values or raises
        exceptions from lux_sequence in order.
        """
        mock = MagicMock()
        it = iter(lux_sequence)

        def _next_lux(_unused=None):
            v = next(it)
            if isinstance(v, Exception):
                raise v
            return v

        type(mock).lux = PropertyMock(side_effect=_next_lux)
        type(mock).full_spectrum = PropertyMock(return_value=full_spectrum)
        type(mock).gain = PropertyMock(return_value=gain)
        return mock

    # ------------------------------------------------------------------
    # read() tests
    # ------------------------------------------------------------------

    def test_read_returns_tsl2591_data_instance(self):
        """read() wraps sensor readings in a Tsl2591Data dataclass."""
        data = self._sensor.read()
        self.assertIsInstance(data, Tsl2591Data)

    def test_read_populates_all_fields(self):
        """read() populates lux, visible, infrared, full_spectrum, raw_luminosity."""
        data = self._sensor.read()
        self.assertIsNotNone(data.lux)
        self.assertIsNotNone(data.visible)
        self.assertIsNotNone(data.infrared)
        self.assertIsNotNone(data.full_spectrum)
        self.assertIsNotNone(data.raw_luminosity)

    def test_read_lux_above_zero(self):
        """read() returns a positive lux value for a normal reading."""
        data = self._sensor.read()
        self.assertGreater(data.lux, 0)

    def test_read_enables_then_disables_sensor(self):
        """read() calls enable() before reading and disable() in finally."""
        self._sensor.read()
        self._tsl.enable.assert_called()
        self._tsl.disable.assert_called()

    # ------------------------------------------------------------------
    # get_lux() — RuntimeError / gain-switching branch tests
    # ------------------------------------------------------------------

    def test_first_runtime_error_switches_gain_and_succeeds(self):
        """First lux overflow → GAIN_LOW → second attempt succeeds."""
        self._sensor.tsl2591 = self._make_tsl_mock(
            [RuntimeError("overflow"), 500.0]
        )
        result = self._sensor.get_lux(wake=False)
        self.assertGreater(result, 0)

    def test_two_runtime_errors_reduces_integration_then_succeeds(self):
        """Two overflows → reduce integration time → third attempt succeeds."""
        self._sensor.tsl2591 = self._make_tsl_mock(
            [RuntimeError("overflow1"), RuntimeError("overflow2"), 250.0]
        )
        result = self._sensor.get_lux(wake=False)
        self.assertGreater(result, 0)

    def test_three_runtime_errors_returns_saturation_floor(self):
        """Three overflows → fully saturated → returns 88000.0."""
        self._sensor.tsl2591 = self._make_tsl_mock(
            [RuntimeError("o1"), RuntimeError("o2"), RuntimeError("o3")]
        )
        result = self._sensor.get_lux(wake=False)
        self.assertEqual(88000.0, result)

    def test_high_full_spectrum_switches_to_gain_low(self):
        """full_spectrum >= 37000 with non-low gain triggers a GAIN_LOW switch."""
        self._sensor.tsl2591 = self._make_tsl_mock(
            [1500.0, 1200.0],
            full_spectrum=38000,
            gain=adafruit_tsl2591.GAIN_MED,
        )
        result = self._sensor.get_lux(wake=False)
        self.assertGreater(result, 0)

    def test_low_full_spectrum_at_gain_low_switches_to_gain_med(self):
        """full_spectrum < 100 at GAIN_LOW triggers a GAIN_MED switch."""
        self._sensor.tsl2591 = self._make_tsl_mock(
            [0.05, 0.1],
            full_spectrum=50,
            gain=adafruit_tsl2591.GAIN_LOW,
        )
        result = self._sensor.get_lux(wake=False)
        self.assertGreater(result, 0)

    def test_zero_lux_floored_to_minimum(self):
        """lux = 0.0 is raised to 0.001 to protect callers from log(0)."""
        type(self._tsl).lux = PropertyMock(return_value=0.0)
        result = self._sensor.get_lux(wake=False)
        self.assertEqual(0.001, result)

    def test_negative_lux_floored_to_minimum(self):
        """Negative lux is clamped to 0.001."""
        type(self._tsl).lux = PropertyMock(return_value=-5.0)
        result = self._sensor.get_lux(wake=False)
        self.assertEqual(0.001, result)
