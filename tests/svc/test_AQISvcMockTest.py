import unittest
from unittest.mock import MagicMock, call, patch

from entity.AQISensor import AQISensor
from svc.AQISvc import AQISvc


class AQISvcMockTest(unittest.TestCase):
    """
    Unit tests for AQISvc with all I2C hardware and database dependencies mocked.

    Hm3301Reader, AQISensorRepository, AppConfig, and time are all patched
    so no physical sensor or database is required.  The singleton is reset
    before and after every test to ensure isolation.
    """

    # ------------------------------------------------------------------
    # Fixture
    # ------------------------------------------------------------------

    def setUp(self):
        AQISvc.inst = None
        AQISvc.inited = False

        self._patcher_reader = patch("svc.AQISvc.Hm3301Reader")
        self._patcher_repo   = patch("svc.AQISvc.AQISensorRepository")
        self._patcher_config = patch("svc.AQISvc.AppConfig")
        self._patcher_time   = patch("svc.AQISvc.time")

        mock_reader_cls  = self._patcher_reader.start()
        mock_repo_cls    = self._patcher_repo.start()
        mock_config_cls  = self._patcher_config.start()
        self._patcher_time.start()

        self._mock_aqi_config = MagicMock()
        self._mock_aqi_config.ceiling = 500
        self._mock_aqi_config.poll    = 3
        mock_config_cls.return_value.aqi = self._mock_aqi_config

        self._mock_reader = MagicMock()
        mock_reader_cls.return_value = self._mock_reader

        self._mock_repo = MagicMock()
        mock_repo_cls.return_value = self._mock_repo

        # Default sensor reading — all fields populated, not high
        self._mock_data = MagicMock()
        self._mock_data.high.return_value = False
        self._mock_data.pm_1_0_conctrt_std   = 10
        self._mock_data.pm_2_5_conctrt_std   = 20
        self._mock_data.pm_10_conctrt_std    = 30
        self._mock_data.pm_1_0_conctrt_atmosph = 11
        self._mock_data.pm_2_5_conctrt_atmosph = 21
        self._mock_data.pm_10_conctrt_atmosph  = 31
        self._mock_reader.read.return_value = self._mock_data

        self._svc = AQISvc()

    def tearDown(self):
        self._patcher_reader.stop()
        self._patcher_repo.stop()
        self._patcher_config.stop()
        self._patcher_time.stop()
        AQISvc.inst = None
        AQISvc.inited = False

    def _inserted_entity(self) -> AQISensor:
        """Return the AQISensor passed to repo.insert() after process() runs."""
        return self._mock_repo.insert.call_args[0][0]

    # ------------------------------------------------------------------
    # process() — field mapping
    # ------------------------------------------------------------------

    def test_process_maps_all_pm_std_fields(self):
        """process() copies all standard PM channel values from sensor data to entity."""
        self._svc.process()
        ent = self._inserted_entity()
        self.assertEqual(10, ent.pm_1_0_conctrt_std)
        self.assertEqual(20, ent.pm_2_5_conctrt_std)
        self.assertEqual(30, ent.pm_10_conctrt_std)

    def test_process_maps_all_pm_atmospheric_fields(self):
        """process() copies all atmospheric PM channel values from sensor data to entity."""
        self._svc.process()
        ent = self._inserted_entity()
        self.assertEqual(11, ent.pm_1_0_conctrt_atmosph)
        self.assertEqual(21, ent.pm_2_5_conctrt_atmosph)
        self.assertEqual(31, ent.pm_10_conctrt_atmosph)

    def test_process_sets_read_time(self):
        """process() sets a non-None read_time on the persisted entity."""
        self._svc.process()
        ent = self._inserted_entity()
        self.assertIsNotNone(ent.read_time)

    def test_process_inserts_aqisensor_entity(self):
        """process() calls repo.insert() with an AQISensor instance."""
        self._svc.process()
        self._mock_repo.insert.assert_called_once()
        self.assertIsInstance(self._inserted_entity(), AQISensor)

    # ------------------------------------------------------------------
    # process() — clean / error handling
    # ------------------------------------------------------------------

    def test_process_calls_clean_after_insert(self):
        """process() calls repo.clean() after a successful insert."""
        self._svc.process()
        self._mock_repo.insert.assert_called_once()
        self._mock_repo.clean.assert_called_once()

    def test_process_swallows_sensor_exception(self):
        """process() catches all exceptions and does not propagate them."""
        self._mock_reader.read.side_effect = RuntimeError("sensor error")
        try:
            self._svc.process()
        except Exception:
            self.fail("process() should not raise exceptions to the caller")

    def test_process_does_not_insert_when_read_raises(self):
        """process() skips repo.insert() when the sensor read fails."""
        self._mock_reader.read.side_effect = RuntimeError("sensor error")
        self._svc.process()
        self._mock_repo.insert.assert_not_called()

    def test_process_does_not_clean_when_read_raises(self):
        """process() skips repo.clean() when the sensor read fails."""
        self._mock_reader.read.side_effect = RuntimeError("sensor error")
        self._svc.process()
        self._mock_repo.clean.assert_not_called()

    # ------------------------------------------------------------------
    # read() — not-high path
    # ------------------------------------------------------------------

    def test_read_returns_data_directly_when_not_high(self):
        """read() returns the sensor data without extra polls when not high."""
        result = self._svc.read()
        self.assertIs(self._mock_data, result)
        self._mock_reader.read.assert_called_once()

    def test_read_does_not_call_lower_when_not_high(self):
        """read() skips the polling loop entirely when data.high() is False."""
        self._svc.read()
        self._mock_data.lower.assert_not_called()

    # ------------------------------------------------------------------
    # read() — high-value polling
    # ------------------------------------------------------------------

    def test_read_calls_lower_when_data_is_high(self):
        """read() calls d.lower() at least once when data starts high."""
        self._mock_data.high.side_effect = [True, False]
        self._svc.read()
        self._mock_data.lower.assert_called()

    def test_read_stops_polling_early_once_data_normalises(self):
        """read() breaks out of the poll loop as soon as d.high() returns False."""
        self._mock_aqi_config.poll = 5
        # high: True enters loop; False on first in-loop check → break after 1 lower
        self._mock_data.high.side_effect = [True, False]
        self._svc.read()
        self.assertEqual(1, self._mock_data.lower.call_count)

    def test_read_polls_up_to_config_limit_when_always_high(self):
        """read() runs the full poll count when data never normalises."""
        self._mock_aqi_config.poll = 3
        self._mock_data.high.return_value = True
        self._svc.read()
        self.assertEqual(3, self._mock_data.lower.call_count)

    def test_read_passes_ceiling_to_lower(self):
        """read() passes the configured ceiling value to d.lower()."""
        self._mock_data.high.side_effect = [True, False]
        self._svc.read()
        _, ceiling_arg = self._mock_data.lower.call_args[0][1], self._mock_data.lower.call_args[0][1]
        self.assertEqual(500, ceiling_arg)
