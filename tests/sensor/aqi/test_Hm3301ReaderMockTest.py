import unittest
from unittest.mock import MagicMock, patch

import pytest

from sensor.aqi.Hm3301Data import Hm3301Data
from sensor.aqi.Hm3301Reader import Hm3301Reader


class Hm3301ReaderMockTest(unittest.TestCase):
    """
    Unit tests for Hm3301Reader with all SMBus I2C hardware mocked out.

    SMBus, i2c_msg, AppConfig, and time are all patched so no physical
    sensor or Pi GPIO is required.  The singleton is reset before and
    after every test to ensure isolation.
    """

    # ------------------------------------------------------------------
    # Raw-packet helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_raw(
        pm_1_0_std=10, pm_2_5_std=20, pm_10_std=30,
        pm_1_0_atm=11, pm_2_5_atm=21, pm_10_atm=31,
    ):
        """Build a 29-byte packet with correct CRC at byte 28."""
        raw = [0] * 29
        raw[4]  = (pm_1_0_std >> 8) & 0xFF;  raw[5]  = pm_1_0_std & 0xFF
        raw[6]  = (pm_2_5_std >> 8) & 0xFF;  raw[7]  = pm_2_5_std & 0xFF
        raw[8]  = (pm_10_std  >> 8) & 0xFF;  raw[9]  = pm_10_std  & 0xFF
        raw[10] = (pm_1_0_atm >> 8) & 0xFF;  raw[11] = pm_1_0_atm & 0xFF
        raw[12] = (pm_2_5_atm >> 8) & 0xFF;  raw[13] = pm_2_5_atm & 0xFF
        raw[14] = (pm_10_atm  >> 8) & 0xFF;  raw[15] = pm_10_atm  & 0xFF
        raw[28] = sum(raw[:28]) & 0xFF
        return raw

    @staticmethod
    def _bad_raw():
        """Return a 29-byte packet whose CRC will fail (byte 28 = 0xFF, sum = 0)."""
        raw = [0] * 29
        raw[28] = 0xFF
        return raw

    # ------------------------------------------------------------------
    # Fixture
    # ------------------------------------------------------------------

    def setUp(self):
        Hm3301Reader.inst = None
        Hm3301Reader.inited = False

        self._patcher_config   = patch("sensor.aqi.Hm3301Reader.AppConfig")
        self._patcher_smbus    = patch("sensor.aqi.Hm3301Reader.SMBus")
        self._patcher_i2c_msg  = patch("sensor.aqi.Hm3301Reader.i2c_msg")
        self._patcher_time     = patch("sensor.aqi.Hm3301Reader.time")

        mock_config_cls        = self._patcher_config.start()
        self._patcher_smbus.start()
        self._mock_i2c_msg     = self._patcher_i2c_msg.start()
        self._patcher_time.start()

        self._mock_aqi_config = MagicMock()
        self._mock_aqi_config.retry = 1
        self._mock_aqi_config.wait_sec = 0
        mock_config_cls.return_value.aqi = self._mock_aqi_config

        # Default: a single valid packet
        self._mock_i2c_msg.read.return_value = self._make_raw()

        self._reader = Hm3301Reader()

    def tearDown(self):
        self._patcher_config.stop()
        self._patcher_smbus.stop()
        self._patcher_i2c_msg.stop()
        self._patcher_time.stop()
        Hm3301Reader.inst = None
        Hm3301Reader.inited = False

    # ------------------------------------------------------------------
    # read() — happy path
    # ------------------------------------------------------------------

    def test_read_returns_hm3301_data_instance(self):
        """read() with a valid CRC packet returns an Hm3301Data object."""
        data = self._reader.read()
        self.assertIsInstance(data, Hm3301Data)

    def test_read_parses_pm_std_values(self):
        """read() correctly unpacks standard PM channels from byte pairs."""
        raw = self._make_raw(pm_1_0_std=10, pm_2_5_std=20, pm_10_std=30)
        self._mock_i2c_msg.read.return_value = raw
        data = self._reader.read()
        self.assertEqual(10, data.pm_1_0_conctrt_std)
        self.assertEqual(20, data.pm_2_5_conctrt_std)
        self.assertEqual(30, data.pm_10_conctrt_std)

    def test_read_parses_pm_atmospheric_values(self):
        """read() correctly unpacks atmospheric PM channels from byte pairs."""
        raw = self._make_raw(pm_1_0_atm=11, pm_2_5_atm=21, pm_10_atm=31)
        self._mock_i2c_msg.read.return_value = raw
        data = self._reader.read()
        self.assertEqual(11, data.pm_1_0_conctrt_atmosph)
        self.assertEqual(21, data.pm_2_5_conctrt_atmosph)
        self.assertEqual(31, data.pm_10_conctrt_atmosph)

    def test_read_parses_large_values_across_byte_boundary(self):
        """16-bit values spanning both high and low bytes are unpacked correctly."""
        raw = self._make_raw(pm_2_5_std=0x0155)  # 341 = 0x01 << 8 | 0x55
        self._mock_i2c_msg.read.return_value = raw
        data = self._reader.read()
        self.assertEqual(0x0155, data.pm_2_5_conctrt_std)

    def test_read_sends_select_write_command(self):
        """read() issues the SELECT_I2C_ADDR write command before reading."""
        self._reader.read()
        self._mock_i2c_msg.write.assert_called_with(
            Hm3301Reader.HM3301_DEFAULT_I2C_ADDR,
            [Hm3301Reader.SELECT_I2C_ADDR],
        )

    def test_read_calls_i2c_read_for_data(self):
        """read() requests DATA_CNT bytes from the sensor address."""
        self._reader.read()
        self._mock_i2c_msg.read.assert_called_with(
            Hm3301Reader.HM3301_DEFAULT_I2C_ADDR,
            Hm3301Reader.DATA_CNT,
        )

    # ------------------------------------------------------------------
    # read() — CRC / retry behaviour
    # ------------------------------------------------------------------

    def test_read_crc_fail_then_success_returns_data(self):
        """A bad CRC on the first read is retried; a good second read succeeds."""
        self._mock_aqi_config.retry = 2
        self._mock_i2c_msg.read.side_effect = [
            self._bad_raw(),
            self._make_raw(pm_2_5_std=55),
        ]
        data = self._reader.read()
        self.assertEqual(55, data.pm_2_5_conctrt_std)

    def test_read_raises_when_retry_is_zero(self):
        """With retry=0 the loop body never runs; raises ValueError."""
        self._mock_aqi_config.retry = 0
        with self.assertRaises(ValueError, msg="retry exceeded"):
            self._reader.read()

    def test_read_raises_after_retries_exhausted_on_persistent_crc_fail(self):
        """Persistent CRC failures stop after `retry` attempts and raise."""
        self._mock_aqi_config.retry = 3
        self._mock_i2c_msg.read.side_effect = [self._bad_raw() for _ in range(10)]
        with self.assertRaises(ValueError, msg="retry exceeded"):
            self._reader.read()
        # the read is bounded by the configured retry count, no infinite loop
        self.assertEqual(3, self._mock_i2c_msg.read.call_count)

    def test_read_retries_on_i2c_oserror_then_succeeds(self):
        """An OSError on the bus is retried rather than propagated."""
        self._mock_aqi_config.retry = 2
        self._mock_i2c_msg.read.side_effect = [
            OSError("i2c read error"),
            self._make_raw(pm_2_5_std=42),
        ]
        data = self._reader.read()
        self.assertEqual(42, data.pm_2_5_conctrt_std)

    def test_read_warms_up_sensor_only_once_across_reads(self):
        """The 0x88 select / warm-up is issued once, not on every read."""
        self._reader.read()
        self._reader.read()
        self._reader.read()
        self.assertEqual(1, self._mock_i2c_msg.write.call_count)


class Hm3301DataTest(unittest.TestCase):
    """Unit tests for Hm3301Data helper methods — no hardware required."""

    def _make_data(self, std=(2, 3, 4), atm=(5, 6, 7)):
        d = Hm3301Data()
        d.pm_1_0_conctrt_std, d.pm_2_5_conctrt_std, d.pm_10_conctrt_std = std
        d.pm_1_0_conctrt_atmosph, d.pm_2_5_conctrt_atmosph, d.pm_10_conctrt_atmosph = atm
        return d

    # lower()

    def test_lower_replaces_values_above_ceiling(self):
        d1 = self._make_data(std=(2, 3, 4), atm=(5, 6, 7))
        d2 = self._make_data(std=(1, 2, 3), atm=(4, 5, 6))
        d1.lower(d2, ceiling=0)
        self.assertEqual(1, d1.pm_1_0_conctrt_std)
        self.assertEqual(2, d1.pm_2_5_conctrt_std)
        self.assertEqual(3, d1.pm_10_conctrt_std)
        self.assertEqual(4, d1.pm_1_0_conctrt_atmosph)
        self.assertEqual(5, d1.pm_2_5_conctrt_atmosph)
        self.assertEqual(6, d1.pm_10_conctrt_atmosph)

    def test_lower_keeps_value_at_or_below_ceiling(self):
        """Values at or below ceiling are not replaced."""
        d1 = self._make_data(std=(5, 5, 5), atm=(5, 5, 5))
        d2 = self._make_data(std=(1, 1, 1), atm=(1, 1, 1))
        d1.lower(d2, ceiling=10)
        # All d1 values are <= ceiling=10, so none replaced
        self.assertEqual(5, d1.pm_1_0_conctrt_std)
        self.assertEqual(5, d1.pm_2_5_conctrt_std)

    # high()

    def test_high_returns_true_when_any_value_exceeds_ceiling(self):
        d = self._make_data(std=(1, 999, 1), atm=(1, 1, 1))
        self.assertTrue(d.high(ceiling=100))

    def test_high_returns_false_when_all_values_at_or_below_ceiling(self):
        d = self._make_data(std=(10, 10, 10), atm=(10, 10, 10))
        self.assertFalse(d.high(ceiling=100))

    def test_high_returns_false_when_all_values_equal_ceiling(self):
        d = self._make_data(std=(5, 5, 5), atm=(5, 5, 5))
        self.assertFalse(d.high(ceiling=5))
