import unittest
from unittest.mock import MagicMock, PropertyMock, call, patch

from gps.GPSData import GPSData
from gps.GPSReader import GPSReader


class GPSReaderMockTest(unittest.TestCase):
    """
    Unit tests for GPSReader with all serial / GPS hardware mocked out.

    serial.Serial, adafruit_gps.GPS, AppConfig, time, and Converter are
    all patched so no physical UART or GPS receiver is required.  The
    singleton is reset before and after every test to ensure isolation.
    """

    # ------------------------------------------------------------------
    # Fixture
    # ------------------------------------------------------------------

    def setUp(self):
        GPSReader.inst = None
        GPSReader.inited = False

        self._patcher_config    = patch("gps.GPSReader.AppConfig")
        self._patcher_serial    = patch("gps.GPSReader.serial")
        self._patcher_gps_mod   = patch("gps.GPSReader.adafruit_gps")
        self._patcher_time      = patch("gps.GPSReader.time")
        self._patcher_converter = patch("gps.GPSReader.Converter")

        mock_config_cls          = self._patcher_config.start()
        self._mock_serial_mod    = self._patcher_serial.start()
        self._mock_gps_mod       = self._patcher_gps_mod.start()
        self._mock_time          = self._patcher_time.start()
        self._mock_converter     = self._patcher_converter.start()

        # Config
        self._mock_gps_config = MagicMock()
        self._mock_gps_config.serial_device = "/dev/ttyS0"
        self._mock_gps_config.baud_rate = 9600
        self._mock_gps_config.init_timeout = 30
        mock_config_cls.return_value.gps = self._mock_gps_config

        # serial.Serial instance — not a context manager, close() in finally
        self._mock_uart = MagicMock()
        self._mock_serial_mod.Serial.return_value = self._mock_uart

        # adafruit_gps.GPS instance with an immediate fix
        self._mock_gps = MagicMock()
        type(self._mock_gps).has_fix    = PropertyMock(return_value=True)
        type(self._mock_gps).latitude   = PropertyMock(return_value=43.6532)
        type(self._mock_gps).longitude  = PropertyMock(return_value=-89.3985)
        type(self._mock_gps).altitude_m = PropertyMock(return_value=270.0)
        self._mock_gps_mod.GPS.return_value = self._mock_gps

        # Converter returns 0 by default (well within any timeout)
        self._mock_converter.duration_seconds.return_value = 0

        self._reader = GPSReader()

    def tearDown(self):
        self._patcher_config.stop()
        self._patcher_serial.stop()
        self._patcher_gps_mod.stop()
        self._patcher_time.stop()
        self._patcher_converter.stop()
        GPSReader.inst = None
        GPSReader.inited = False

    # ------------------------------------------------------------------
    # read() — happy path
    # ------------------------------------------------------------------

    def test_read_returns_gps_data_instance(self):
        """read() with an immediate fix returns a GPSData object."""
        data = self._reader.read()
        self.assertIsInstance(data, GPSData)

    def test_read_maps_latitude(self):
        """read() passes gps.latitude to GPSData."""
        data = self._reader.read()
        self.assertEqual(43.6532, data.latitude)

    def test_read_maps_longitude(self):
        """read() passes gps.longitude to GPSData."""
        data = self._reader.read()
        self.assertEqual(-89.3985, data.longitude)

    def test_read_maps_altitude(self):
        """read() passes gps.altitude_m to GPSData."""
        data = self._reader.read()
        self.assertEqual(270.0, data.altitude)

    def test_read_opens_serial_with_config_params(self):
        """read() opens the UART using the device and baud rate from config."""
        self._reader.read()
        self._mock_serial_mod.Serial.assert_called_once_with(
            "/dev/ttyS0", baudrate=9600, timeout=1
        )

    def test_read_sends_nmea_output_command(self):
        """read() configures NMEA output sentences via PMTK314."""
        self._reader.read()
        self._mock_gps.send_command.assert_any_call(
            b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0"
        )

    def test_read_sends_nmea_update_rate_command(self):
        """read() sets the NMEA update rate via PMTK220."""
        self._reader.read()
        self._mock_gps.send_command.assert_any_call(b"PMTK220,1000")

    def test_read_calls_gps_update_after_commands(self):
        """read() calls gps.update() at least once after sending setup commands."""
        self._reader.read()
        self._mock_gps.update.assert_called()

    def test_read_closes_uart_in_finally(self):
        """read() always closes the serial port, even on success."""
        self._reader.read()
        self._mock_uart.close.assert_called_once()

    # ------------------------------------------------------------------
    # read() — fix-wait loop
    # ------------------------------------------------------------------

    def test_read_waits_in_loop_until_fix_acquired(self):
        """read() loops calling gps.update() until has_fix becomes True."""
        # has_fix: False (while-entry), False (re-check in loop),
        #          True (while-entry exits), True (post-loop check)
        type(self._mock_gps).has_fix = PropertyMock(
            side_effect=[False, False, True, True]
        )
        data = self._reader.read()
        self.assertIsInstance(data, GPSData)
        self.assertGreaterEqual(self._mock_gps.update.call_count, 2)

    def test_read_raises_ioerror_when_fix_times_out(self):
        """read() raises IOError when the fix is not acquired within init_timeout."""
        type(self._mock_gps).has_fix = PropertyMock(return_value=False)
        self._mock_converter.duration_seconds.return_value = (
            self._mock_gps_config.init_timeout + 1
        )
        with self.assertRaises(IOError):
            self._reader.read()

    def test_read_closes_uart_even_on_timeout_error(self):
        """uart.close() is called in the finally block even when IOError is raised."""
        type(self._mock_gps).has_fix = PropertyMock(return_value=False)
        self._mock_converter.duration_seconds.return_value = (
            self._mock_gps_config.init_timeout + 1
        )
        with self.assertRaises(IOError):
            self._reader.read()
        self._mock_uart.close.assert_called_once()
