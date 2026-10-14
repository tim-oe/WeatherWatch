import unittest
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import svc.SchedulerSvc as scheduler_module
from svc.SchedulerSvc import SchedulerSvc


# ---------------------------------------------------------------------------
# Module-level task functions — each just constructs a svc and calls process
# ---------------------------------------------------------------------------

class SchedulerModuleFunctionsTest(unittest.TestCase):

    @patch("svc.SchedulerSvc.SensorSvc")
    def test_sensor_calls_process(self, MockSvc):
        scheduler_module.sensor()
        MockSvc.return_value.process.assert_called_once()

    @patch("svc.SchedulerSvc.WUSvc")
    def test_wu_calls_process(self, MockSvc):
        scheduler_module.wu()
        MockSvc.return_value.process.assert_called_once()

    @patch("svc.SchedulerSvc.AQISvc")
    def test_aqi_calls_process(self, MockSvc):
        scheduler_module.aqi()
        MockSvc.return_value.process.assert_called_once()

    @patch("svc.SchedulerSvc.CameraSvc")
    def test_camera_calls_process(self, MockSvc):
        scheduler_module.camera()
        MockSvc.return_value.process.assert_called_once()

    @patch("svc.SchedulerSvc.BackupSvc")
    def test_file_backup_calls_camera(self, MockSvc):
        scheduler_module.file_backup()
        MockSvc.return_value.camera.assert_called_once()

    @patch("svc.SchedulerSvc.DBFlushSvc")
    def test_db_flush_calls_process(self, MockSvc):
        scheduler_module.db_flush()
        MockSvc.return_value.process.assert_called_once()

    @patch("svc.SchedulerSvc.TimelapseSvc")
    def test_timelapse_calls_process(self, MockSvc):
        scheduler_module.timelapse()
        MockSvc.return_value.process.assert_called_once()

    @patch("svc.SchedulerSvc.PIMetricsSvc")
    def test_pimetrics_calls_process(self, MockSvc):
        scheduler_module.pimetrics()
        MockSvc.return_value.process.assert_called_once()


# ---------------------------------------------------------------------------
# SchedulerSvc instance methods
# ---------------------------------------------------------------------------

class SchedulerSvcTest(unittest.TestCase):

    def setUp(self):
        self.svc: SchedulerSvc = SchedulerSvc()

    @contextmanager
    def _swap_config(self, mock_cfg):
        """Temporarily replace _app_config on the singleton."""
        original = self.svc._app_config
        self.svc._app_config = mock_cfg
        try:
            yield mock_cfg
        finally:
            self.svc._app_config = original

    def test_str_returns_string(self):
        result = str(self.svc)
        self.assertIsInstance(result, str)

    def test_start_and_pause(self):
        self.svc.start()
        self.svc.pause()

    # ------------------------------------------------------------------
    # init_camera
    # ------------------------------------------------------------------

    def test_init_camera_disabled_does_not_add(self):
        cfg = MagicMock()
        cfg.camera.enable = False
        with self._swap_config(cfg):
            with patch.object(self.svc._scheduler, "add_job") as mock_add:
                self.svc.init_camera()
        mock_add.assert_not_called()

    # ------------------------------------------------------------------
    # init_timelapse
    # ------------------------------------------------------------------

    def test_init_timelapse_disabled_does_not_add(self):
        cfg = MagicMock()
        cfg.timelapse.enable = False
        with self._swap_config(cfg):
            with patch.object(self.svc._scheduler, "add_job") as mock_add:
                self.svc.init_timelapse()
        mock_add.assert_not_called()

    # ------------------------------------------------------------------
    # init_backup_file
    # ------------------------------------------------------------------

    def test_init_backup_file_disabled_does_not_add(self):
        cfg = MagicMock()
        cfg.backup.file_enable = False
        with self._swap_config(cfg):
            with patch.object(self.svc._scheduler, "add_job") as mock_add:
                self.svc.init_backup_file()
        mock_add.assert_not_called()

    def test_db_flush_job_is_registered(self):
        self.assertIsNotNone(self.svc._scheduler.get_job(SchedulerSvc.DB_FLUSH_JOB))

    # ------------------------------------------------------------------
    # init_aqi
    # ------------------------------------------------------------------

    def test_init_aqi_disabled_does_not_add(self):
        cfg = MagicMock()
        cfg.aqi.enable = False
        with self._swap_config(cfg):
            with patch.object(self.svc._scheduler, "add_job") as mock_add:
                self.svc.init_aqi()
        mock_add.assert_not_called()

    # ------------------------------------------------------------------
    # init_wu
    # ------------------------------------------------------------------

    def test_init_wu_disabled_does_not_add(self):
        cfg = MagicMock()
        cfg.wu.enable = False
        with self._swap_config(cfg):
            with patch.object(self.svc._scheduler, "add_job") as mock_add:
                self.svc.init_wu()
        mock_add.assert_not_called()

    def test_del_shuts_down_scheduler(self):
        """Calling __del__ directly invokes _scheduler.shutdown()."""
        with patch.object(self.svc._scheduler, "shutdown") as mock_shutdown:
            self.svc.__del__()
        mock_shutdown.assert_called_once()

    def test_str_via_direct_method_call(self):
        """Calling __str__ directly (bypassing the @logger override) covers lines 298-301."""
        from svc.SchedulerSvc import SchedulerSvc as _Svc
        result = _Svc.__str__(self.svc)
        self.assertIsInstance(result, str)
