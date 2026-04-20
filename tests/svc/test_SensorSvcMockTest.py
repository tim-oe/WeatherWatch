import json
import unittest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

from sensor.sdr.IndoorData import IndoorData
from sensor.sdr.OutdoorData import OutdoorData
from svc.SensorSvc import SensorSvc


def _load_indoor(path: str) -> IndoorData:
    with open(path) as f:
        return json.load(f, object_hook=IndoorData.json_decoder)


def _load_outdoor(path: str) -> OutdoorData:
    with open(path) as f:
        raw = json.load(f)
    with open(path) as f:
        data: OutdoorData = json.load(f, object_hook=OutdoorData.json_decoder)
    data.raw = raw
    return data


class SensorSvcMockTest(unittest.TestCase):
    """Unit tests for SensorSvc handler methods using mock sensor data from the data/ folder.

    All external dependencies (repositories, hardware readers, EventBus) are mocked so
    no database connection or physical sensors are required.
    """

    def setUp(self):
        SensorSvc.inst = None
        SensorSvc.inited = False

        self._patcher_sdr = patch("svc.SensorSvc.SDRReader")
        self._patcher_bmp = patch("svc.SensorSvc.Bmp388SensorReader")
        self._patcher_light_reader = patch("svc.SensorSvc.Tsl2591SensorReader")
        self._patcher_indoor_repo = patch("svc.SensorSvc.IndoorSensorRepository")
        self._patcher_outdoor_repo = patch("svc.SensorSvc.OutdoorSensorRepository")
        self._patcher_light_repo = patch("svc.SensorSvc.LightSensorRepository")
        self._patcher_eventbus = patch("svc.SensorSvc.EventBus")

        self._mock_sdr_cls = self._patcher_sdr.start()
        self._mock_bmp_cls = self._patcher_bmp.start()
        self._patcher_light_reader.start()
        self._mock_indoor_repo_cls = self._patcher_indoor_repo.start()
        self._mock_outdoor_repo_cls = self._patcher_outdoor_repo.start()
        self._patcher_light_repo.start()
        self._patcher_eventbus.start()

        # Capture repo instances returned by the mock constructors
        self._mock_indoor_repo = MagicMock()
        self._mock_outdoor_repo = MagicMock()
        self._mock_indoor_repo_cls.return_value = self._mock_indoor_repo
        self._mock_outdoor_repo_cls.return_value = self._mock_outdoor_repo

        # Default: no previous outdoor reading
        self._mock_outdoor_repo.find_latest.return_value = None

        # BMP reader returns a mock with a pressure value
        mock_bmp_data = MagicMock()
        mock_bmp_data.pressure = 1013.25
        self._mock_bmp_cls.return_value.read.return_value = mock_bmp_data

        self.svc = SensorSvc()

    def tearDown(self):
        self._patcher_sdr.stop()
        self._patcher_bmp.stop()
        self._patcher_light_reader.stop()
        self._patcher_indoor_repo.stop()
        self._patcher_outdoor_repo.stop()
        self._patcher_light_repo.stop()
        self._patcher_eventbus.stop()
        SensorSvc.inst = None
        SensorSvc.inited = False

    # ------------------------------------------------------------------
    # handle_indoor tests
    # ------------------------------------------------------------------

    def test_handle_indoor_3dfloor_saves_entity(self):
        """handle_indoor maps IndoorData fields onto an IndoorSensor entity and inserts it."""
        data = _load_indoor("data/indoor_3dfloor.json")

        self.svc.handle_indoor(data)

        self._mock_indoor_repo.insert.assert_called_once()
        ent = self._mock_indoor_repo.insert.call_args[0][0]
        self.assertEqual(169, ent.sensor_id)
        self.assertEqual(2, ent.channel)
        self.assertAlmostEqual(64.9, ent.temperature_f)
        self.assertEqual(40, ent.humidity)
        self.assertTrue(ent.battery_ok)

    def test_handle_indoor_basement_saves_entity(self):
        """handle_indoor saves basement sensor data with correct channel and temperature."""
        data = _load_indoor("data/indoor_basement.json")

        self.svc.handle_indoor(data)

        self._mock_indoor_repo.insert.assert_called_once()
        ent = self._mock_indoor_repo.insert.call_args[0][0]
        self.assertEqual(10, ent.sensor_id)
        self.assertEqual(3, ent.channel)
        self.assertAlmostEqual(59.2, ent.temperature_f)
        self.assertEqual(44, ent.humidity)

    # ------------------------------------------------------------------
    # handle_outdoor tests
    # ------------------------------------------------------------------

    def test_handle_outdoor_first_read_delta_zero(self):
        """Rain delta is 0.0 when there is no prior outdoor reading."""
        data = _load_outdoor("data/outdoor.json")
        self._mock_outdoor_repo.find_latest.return_value = None

        self.svc.handle_outdoor(data)

        self._mock_outdoor_repo.insert.assert_called_once()
        ent = self._mock_outdoor_repo.insert.call_args[0][0]
        self.assertEqual(Decimal("0.0"), ent.rain_delta_mm)
        self.assertAlmostEqual(268.8, float(ent.rain_cum_mm))

    def test_handle_outdoor_rain_increase_delta(self):
        """Rain delta reflects the increase since the last reading."""
        prior = MagicMock()
        prior.rain_cum_mm = Decimal("200.0")
        self._mock_outdoor_repo.find_latest.return_value = prior

        data = _load_outdoor("data/outdoor.json")  # rain_mm = 268.8

        self.svc.handle_outdoor(data)

        ent = self._mock_outdoor_repo.insert.call_args[0][0]
        self.assertEqual(Decimal("68.80"), ent.rain_delta_mm)

    def test_handle_outdoor_sensor_reset_uses_cumulative_as_delta(self):
        """When rain_mm decreases (sensor reset), the cumulative value becomes the delta."""
        prior = MagicMock()
        prior.rain_cum_mm = Decimal("500.0")
        self._mock_outdoor_repo.find_latest.return_value = prior

        data = _load_outdoor("data/outdoor.json")  # rain_mm = 268.8 < 500.0

        self.svc.handle_outdoor(data)

        ent = self._mock_outdoor_repo.insert.call_args[0][0]
        self.assertAlmostEqual(268.8, float(ent.rain_delta_mm))

    def test_handle_outdoor_saves_wind_and_light_fields(self):
        """Wind and light fields from OutdoorData are persisted on the entity."""
        data = _load_outdoor("data/outdoor.json")

        self.svc.handle_outdoor(data)

        ent = self._mock_outdoor_repo.insert.call_args[0][0]
        self.assertAlmostEqual(2.0, ent.wind_avg_m_s)
        self.assertAlmostEqual(2.6, ent.wind_max_m_s)
        self.assertEqual(303, ent.wind_dir_deg)
        self.assertEqual(113903, ent.light_lux)
        self.assertAlmostEqual(5.1, ent.uv)

    def test_handle_outdoor_saves_pressure_from_bmp(self):
        """Barometric pressure from BMP reader is stored on the outdoor entity."""
        data = _load_outdoor("data/outdoor.json")

        self.svc.handle_outdoor(data)

        ent = self._mock_outdoor_repo.insert.call_args[0][0]
        self.assertAlmostEqual(1013.25, ent.pressure)
