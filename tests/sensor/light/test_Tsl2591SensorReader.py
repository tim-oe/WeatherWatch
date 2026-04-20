import unittest
from unittest.mock import MagicMock, PropertyMock, patch

import adafruit_tsl2591

from sensor.light.Tsl2591SensorReader import Tsl2591SensorReader


def _get_sensor() -> Tsl2591SensorReader:
    return Tsl2591SensorReader()


class Tsl2591SensorReaderHappyPathTest(unittest.TestCase):

    def test_read_returns_data(self):
        sensor = _get_sensor()
        data = sensor.read()
        self.assertIsNotNone(data)

    def test_get_lux_default(self):
        sensor = _get_sensor()
        lux = sensor.get_lux()
        self.assertGreater(lux, 0)


class Tsl2591SensorReaderGetLuxErrorPathsTest(unittest.TestCase):
    """
    Drive the RuntimeError / gain-switching branches of get_lux() without
    real hardware by patching the tsl2591 attribute on the singleton.
    """

    def _make_tsl_mock(self, lux_sequence, full_spectrum=100, gain=adafruit_tsl2591.GAIN_MED):
        """
        Build a MagicMock that mimics the tsl2591 sensor object.
        lux_sequence: list of values/exceptions to yield on each lux access.
        """
        mock = MagicMock()
        # Use a mutable iterator so each property access advances independently.
        it = iter(lux_sequence)

        def _lux_getter(self_unused=None):
            v = next(it)
            if isinstance(v, Exception):
                raise v
            return v

        type(mock).lux = PropertyMock(side_effect=_lux_getter)
        type(mock).full_spectrum = PropertyMock(return_value=full_spectrum)
        type(mock).gain = PropertyMock(return_value=gain)
        return mock

    # ------------------------------------------------------------------
    # First RuntimeError → switch to GAIN_LOW, second attempt succeeds
    # ------------------------------------------------------------------

    @patch("time.sleep")
    def test_first_runtime_error_switches_gain_and_succeeds(self, _sleep):
        sensor = _get_sensor()
        mock_tsl = self._make_tsl_mock([RuntimeError("overflow"), 500.0])
        original = sensor.tsl2591
        sensor.tsl2591 = mock_tsl
        try:
            result = sensor.get_lux(wake=False)
            self.assertGreater(result, 0)
        finally:
            sensor.tsl2591 = original

    # ------------------------------------------------------------------
    # Two RuntimeErrors → also reduce integration time, third succeeds
    # ------------------------------------------------------------------

    @patch("time.sleep")
    def test_two_runtime_errors_reduces_integration_then_succeeds(self, _sleep):
        sensor = _get_sensor()
        mock_tsl = self._make_tsl_mock(
            [RuntimeError("overflow1"), RuntimeError("overflow2"), 250.0]
        )
        original = sensor.tsl2591
        sensor.tsl2591 = mock_tsl
        try:
            result = sensor.get_lux(wake=False)
            self.assertGreater(result, 0)
        finally:
            sensor.tsl2591 = original

    # ------------------------------------------------------------------
    # Three RuntimeErrors → fully saturated, returns 88000.0
    # ------------------------------------------------------------------

    @patch("time.sleep")
    def test_three_runtime_errors_returns_saturation_floor(self, _sleep):
        sensor = _get_sensor()
        mock_tsl = self._make_tsl_mock(
            [RuntimeError("o1"), RuntimeError("o2"), RuntimeError("o3")]
        )
        original = sensor.tsl2591
        sensor.tsl2591 = mock_tsl
        try:
            result = sensor.get_lux(wake=False)
            self.assertEqual(88000.0, result)
        finally:
            sensor.tsl2591 = original

    # ------------------------------------------------------------------
    # full_spectrum >= 37000 and gain != GAIN_LOW → switch to GAIN_LOW
    # ------------------------------------------------------------------

    @patch("time.sleep")
    def test_high_full_spectrum_switches_to_gain_low(self, _sleep):
        sensor = _get_sensor()
        # First lux read succeeds; full_spectrum is saturated; second lux read after gain switch
        mock_tsl = self._make_tsl_mock(
            [1500.0, 1200.0],
            full_spectrum=38000,
            gain=adafruit_tsl2591.GAIN_MED,
        )
        original = sensor.tsl2591
        sensor.tsl2591 = mock_tsl
        try:
            result = sensor.get_lux(wake=False)
            self.assertGreater(result, 0)
        finally:
            sensor.tsl2591 = original

    # ------------------------------------------------------------------
    # full_spectrum < 100 and gain == GAIN_LOW → switch to GAIN_MED
    # ------------------------------------------------------------------

    @patch("time.sleep")
    def test_low_full_spectrum_at_gain_low_switches_to_gain_med(self, _sleep):
        sensor = _get_sensor()
        mock_tsl = self._make_tsl_mock(
            [0.05, 0.1],
            full_spectrum=50,
            gain=adafruit_tsl2591.GAIN_LOW,
        )
        original = sensor.tsl2591
        sensor.tsl2591 = mock_tsl
        try:
            result = sensor.get_lux(wake=False)
            self.assertGreater(result, 0)
        finally:
            sensor.tsl2591 = original
