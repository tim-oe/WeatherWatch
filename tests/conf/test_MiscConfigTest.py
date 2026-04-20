"""
Tests for config classes that don't have dedicated test files.
Covers missing property getter lines in BackupConfig, GPSConfig, LightConfig,
WUConfig, SchedulerConfig, TimelapseConfig, and AppConfig.
"""
import unittest

from conf.AppConfig import AppConfig


class BackupConfigTest(unittest.TestCase):

    def setUp(self):
        self.cfg = AppConfig().backup

    def test_file_enable(self):
        self.assertIsNotNone(self.cfg.file_enable)

    def test_db_enable(self):
        self.assertIsNotNone(self.cfg.db_enable)

    def test_folder(self):
        self.assertIsNotNone(self.cfg.folder)

    def test_purge_enable(self):
        self.assertIsNotNone(self.cfg.purge_enable)

    def test_img_old(self):
        self.assertIsNotNone(self.cfg.img_old)

    def test_vid_old(self):
        self.assertIsNotNone(self.cfg.vid_old)

    def test_db_weekly_old(self):
        self.assertIsNotNone(self.cfg.db_weekly_old)


class GPSConfigTest(unittest.TestCase):

    def setUp(self):
        self.cfg = AppConfig().gps

    def test_enable(self):
        self.assertIsNotNone(self.cfg.enable)

    def test_serial_device(self):
        self.assertIsNotNone(self.cfg.serial_device)

    def test_baud_rate(self):
        self.assertGreater(self.cfg.baud_rate, 0)

    def test_init_timeout(self):
        self.assertGreater(self.cfg.init_timeout, 0)


class LightConfigTest(unittest.TestCase):

    def test_enable(self):
        cfg = AppConfig().light
        self.assertIsNotNone(cfg.enable)


class WUConfigTest(unittest.TestCase):

    def setUp(self):
        self.cfg = AppConfig().wu

    def test_station_key(self):
        self.assertIsNotNone(self.cfg.station_key)

    def test_api_key(self):
        self.assertIsNotNone(self.cfg.api_key)

    def test_indoor_channel(self):
        self.assertIsNotNone(self.cfg.indoor_channel)


class SchedulerConfigTest(unittest.TestCase):

    def setUp(self):
        self.cfg = AppConfig().scheduler

    def test_aqi_interval(self):
        self.assertGreater(self.cfg.aqi_interval, 0)

    def test_sensor_interval(self):
        self.assertGreater(self.cfg.sensor_interval, 0)

    def test_wu_interval(self):
        self.assertGreater(self.cfg.wu_interval, 0)

    def test_pi_metrics_interval(self):
        self.assertGreater(self.cfg.pi_metrics_interval, 0)

    def test_camera_interval(self):
        self.assertGreater(self.cfg.camera_interval, 0)

    def test_timelapse_hour(self):
        self.assertIsNotNone(self.cfg.timelapse_hour)

    def test_db_back_hour(self):
        self.assertIsNotNone(self.cfg.db_back_hour)

    def test_file_back_hour(self):
        self.assertIsNotNone(self.cfg.file_back_hour)


class TimelapseConfigTest(unittest.TestCase):

    def setUp(self):
        self.cfg = AppConfig().timelapse

    def test_enable(self):
        self.assertIsNotNone(self.cfg.enable)

    def test_frames_per_second(self):
        self.assertGreater(self.cfg.frames_per_second, 0)

    def test_codec(self):
        self.assertIsNotNone(self.cfg.codec)


class AppConfigMiscTest(unittest.TestCase):

    def setUp(self):
        self.ac = AppConfig()

    def test_get_sensor_by_name(self):
        sensors = self.ac.sensors
        if sensors:
            first = sensors[0]
            result = self.ac.get_sensor(first.name)
            self.assertEqual(first.name, result.name)

    def test_ignores_returns_list(self):
        ignores = self.ac.ignores
        self.assertIsInstance(ignores, list)

    def test_get_ignore_by_key(self):
        ignores_dict = self.ac._ignores
        if ignores_dict:
            key = next(iter(ignores_dict))
            result = self.ac.get_ignore(key)
            self.assertIsNotNone(result)

    def test_no_console_env_var_removes_console_handlers(self):
        """When ENVAR_NO_CONSOLE=1, init_logging filters handlers to RotatingFileHandler only."""
        import logging
        import logging.handlers
        from unittest.mock import patch
        from conf.AppConfig import AppConfig

        with patch.dict("os.environ", {AppConfig.ENVAR_NO_CONSOLE: "1"}):
            self.ac.init_logging()
        for h in logging.root.handlers:
            self.assertIsInstance(h, logging.handlers.RotatingFileHandler)
