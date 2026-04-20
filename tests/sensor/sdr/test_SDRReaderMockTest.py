import io
import json
import unittest
from queue import Queue
from unittest.mock import MagicMock, patch

from conf.SensorConfig import SensorConfig
from sensor.sdr.IndoorData import IndoorData
from sensor.sdr.OutdoorData import OutdoorData
from sensor.sdr.SDRReader import SDRReader

_INDOOR_3DFLOOR_KEY = "[Ambientweather-F007TH|169|2]"
_INDOOR_BASEMENT_KEY = "[Ambientweather-F007TH|10|3]"
_OUTDOOR_KEY = "[Cotech-367959|238]"

_SENSOR_CONFIGS = {
    _INDOOR_3DFLOOR_KEY: SensorConfig(
        {"name": "indoor_3dfloor", "model": "Ambientweather-F007TH", "id": 169, "channel": 2, "dataClass": "IndoorData", "device": 20}
    ),
    _INDOOR_BASEMENT_KEY: SensorConfig(
        {"name": "indoor_basement", "model": "Ambientweather-F007TH", "id": 10, "channel": 3, "dataClass": "IndoorData", "device": 20}
    ),
    _OUTDOOR_KEY: SensorConfig(
        {"name": "outdoor", "model": "Cotech-367959", "id": 238, "dataClass": "OutdoorData", "device": 153}
    ),
}


def _load_json_line(path: str) -> str:
    """Load a JSON file and return it as a compact single-line string."""
    with open(path) as f:
        return json.dumps(json.load(f))


class SDRReaderMockTest(unittest.TestCase):
    """Unit tests for SDRReader using mock sensor data from the data/ folder."""

    def setUp(self):
        SDRReader.inst = None
        SDRReader.inited = False

        self._patcher_config = patch("sensor.sdr.SDRReader.AppConfig")
        self._patcher_repo = patch("sensor.sdr.SDRReader.SDRMetricsRepository")
        self._patcher_emailer = patch("sensor.sdr.SDRReader.Emailer")
        self._patcher_eventbus = patch("sensor.sdr.SDRReader.EventBus")

        mock_config_cls = self._patcher_config.start()
        self._patcher_repo.start()
        self._patcher_emailer.start()
        self._patcher_eventbus.start()

        # Match the real class constants so SDRReader.__init__ can index into conf
        mock_config_cls.SDR_KEY = "sdr"
        mock_config_cls.READER_KEY = "reader"

        mock_config = MagicMock()
        mock_config.conf = {"sdr": {"reader": {"timeout": 30}}}
        mock_config.sensors = list(_SENSOR_CONFIGS.values())
        mock_config.ignores = []
        mock_config_cls.return_value = mock_config

    def tearDown(self):
        self._patcher_config.stop()
        self._patcher_repo.stop()
        self._patcher_emailer.stop()
        self._patcher_eventbus.stop()
        SDRReader.inst = None
        SDRReader.inited = False

    # ------------------------------------------------------------------
    # push_record tests
    # ------------------------------------------------------------------

    def test_push_record_valid_json_lines_queued(self):
        """Valid JSON lines are pushed to the queue."""
        reader = SDRReader()
        q = Queue()
        lines = '{"model": "test", "id": 1}\n{"model": "test2", "id": 2}\n'
        reader.push_record(io.StringIO(lines), q)
        self.assertEqual(2, q.qsize())

    def test_push_record_non_json_skipped(self):
        """Non-JSON lines are silently discarded."""
        reader = SDRReader()
        q = Queue()
        lines = 'not json\n{"model": "ok", "id": 9}\nstill not json\n'
        reader.push_record(io.StringIO(lines), q)
        self.assertEqual(1, q.qsize())
        self.assertEqual('{"model": "ok", "id": 9}', q.get())

    # ------------------------------------------------------------------
    # process_record tests
    # ------------------------------------------------------------------

    def test_process_record_indoor_3dfloor(self):
        """Indoor 3rd-floor JSON is decoded into IndoorData with correct field values."""
        reader = SDRReader()
        line = _load_json_line("data/indoor_3dfloor.json")
        reads, processed = [], []
        sensors = {_INDOOR_3DFLOOR_KEY: _SENSOR_CONFIGS[_INDOOR_3DFLOOR_KEY]}

        reader.process_record(line, sensors, reads, processed)

        self.assertEqual(1, len(reads))
        self.assertIsInstance(reads[0], IndoorData)
        self.assertEqual(169, reads[0].sensor_id)
        self.assertEqual(2, reads[0].channel)
        self.assertAlmostEqual(64.9, reads[0].temperature)
        self.assertEqual(40, reads[0].humidity)
        self.assertTrue(reads[0].battery_ok)
        self.assertIsNotNone(reads[0].raw)
        self.assertIsNotNone(reads[0].config)
        self.assertIn(_INDOOR_3DFLOOR_KEY, processed)
        self.assertEqual(0, len(sensors))

    def test_process_record_indoor_basement(self):
        """Indoor basement JSON is decoded into IndoorData with correct field values."""
        reader = SDRReader()
        line = _load_json_line("data/indoor_basement.json")
        reads, processed = [], []
        sensors = {_INDOOR_BASEMENT_KEY: _SENSOR_CONFIGS[_INDOOR_BASEMENT_KEY]}

        reader.process_record(line, sensors, reads, processed)

        self.assertEqual(1, len(reads))
        self.assertIsInstance(reads[0], IndoorData)
        self.assertEqual(10, reads[0].sensor_id)
        self.assertEqual(3, reads[0].channel)
        self.assertAlmostEqual(59.2, reads[0].temperature)
        self.assertEqual(44, reads[0].humidity)
        self.assertIn(_INDOOR_BASEMENT_KEY, processed)

    def test_process_record_outdoor(self):
        """Outdoor JSON is decoded into OutdoorData with correct field values."""
        reader = SDRReader()
        line = _load_json_line("data/outdoor.json")
        reads, processed = [], []
        sensors = {_OUTDOOR_KEY: _SENSOR_CONFIGS[_OUTDOOR_KEY]}

        reader.process_record(line, sensors, reads, processed)

        self.assertEqual(1, len(reads))
        self.assertIsInstance(reads[0], OutdoorData)
        self.assertEqual(238, reads[0].sensor_id)
        self.assertAlmostEqual(58.8, reads[0].temperature)
        self.assertEqual(34, reads[0].humidity)
        self.assertAlmostEqual(268.8, reads[0].rain_mm)
        self.assertEqual(303, reads[0].wind_dir_deg)
        self.assertAlmostEqual(2.0, reads[0].wind_avg_m_s)
        self.assertAlmostEqual(2.6, reads[0].wind_max_m_s)
        self.assertEqual(113903, reads[0].light_lux)
        self.assertAlmostEqual(5.1, reads[0].uv)
        self.assertIn(_OUTDOOR_KEY, processed)

    def test_process_record_ignored_sensor_skipped(self):
        """A sensor whose key is in the ignores list is silently skipped."""
        reader = SDRReader()
        reader._ignores = [_OUTDOOR_KEY]
        line = _load_json_line("data/outdoor.json")
        reads, processed = [], []
        sensors = {_OUTDOOR_KEY: _SENSOR_CONFIGS[_OUTDOOR_KEY]}

        reader.process_record(line, sensors, reads, processed)

        self.assertEqual(0, len(reads))
        self.assertEqual(1, len(sensors))

    def test_process_record_unknown_sensor_no_crash(self):
        """An unregistered sensor key is warned about but does not raise."""
        reader = SDRReader()
        line = _load_json_line("data/outdoor.json")
        reads, processed = [], []

        reader.process_record(line, sensors={}, reads=reads, processed=processed)

        self.assertEqual(0, len(reads))

    def test_process_record_already_processed_key_skipped(self):
        """Second occurrence of an already-processed key is silently ignored."""
        reader = SDRReader()
        line = _load_json_line("data/outdoor.json")
        reads, processed = [], [_OUTDOOR_KEY]

        reader.process_record(line, sensors={}, reads=reads, processed=processed)

        self.assertEqual(0, len(reads))

    # ------------------------------------------------------------------
    # read() end-to-end with mocked Popen
    # ------------------------------------------------------------------

    def test_read_processes_all_three_sensors(self):
        """read() yields one BaseData entry per sensor when Popen returns sample lines."""
        indoor1 = _load_json_line("data/indoor_3dfloor.json") + "\n"
        indoor2 = _load_json_line("data/indoor_basement.json") + "\n"
        outdoor = _load_json_line("data/outdoor.json") + "\n"

        mock_proc = MagicMock()
        mock_proc.__enter__ = MagicMock(return_value=mock_proc)
        mock_proc.__exit__ = MagicMock(return_value=False)
        mock_proc.stdout = iter([indoor1, indoor2, outdoor])

        with patch("sensor.sdr.SDRReader.Popen", return_value=mock_proc):
            reader = SDRReader()
            reader.read()

        self.assertEqual(3, len(reader.reads))
        models = {r.sensor_id for r in reader.reads}
        self.assertIn(169, models)
        self.assertIn(10, models)
        self.assertIn(238, models)

    def test_read_partial_sensors_returns_available_reads(self):
        """read() returns whatever was received when only a subset of sensors respond."""
        outdoor = _load_json_line("data/outdoor.json") + "\n"

        mock_proc = MagicMock()
        mock_proc.__enter__ = MagicMock(return_value=mock_proc)
        mock_proc.__exit__ = MagicMock(return_value=False)
        mock_proc.stdout = iter([outdoor])

        with patch("sensor.sdr.SDRReader.Popen", return_value=mock_proc):
            reader = SDRReader()
            reader.read()

        self.assertEqual(1, len(reader.reads))
        self.assertIsInstance(reader.reads[0], OutdoorData)
