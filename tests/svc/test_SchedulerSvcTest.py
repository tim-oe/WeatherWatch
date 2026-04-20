import unittest
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

from apscheduler.jobstores.base import JobLookupError

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

    @patch("svc.SchedulerSvc.BackupSvc")
    def test_db_backup_calls_db(self, MockSvc):
        scheduler_module.db_backup()
        MockSvc.return_value.db.assert_called_once()

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

    def test_init_camera_disabled_removes_job(self):
        cfg = MagicMock()
        cfg.camera.enable = False
        with self._swap_config(cfg):
            with patch.object(self.svc._jobstore, "remove_job") as mock_remove:
                self.svc.init_camera()
        mock_remove.assert_called_once_with(SchedulerSvc.CAMERA_JOB)

    def test_init_camera_disabled_job_not_found_logged(self):
        cfg = MagicMock()
        cfg.camera.enable = False
        with self._swap_config(cfg):
            with patch.object(self.svc._jobstore, "remove_job",
                              side_effect=JobLookupError(SchedulerSvc.CAMERA_JOB)):
                self.svc.init_camera()  # must not raise

    # ------------------------------------------------------------------
    # init_timelapse
    # ------------------------------------------------------------------

    def test_init_timelapse_disabled_removes_job(self):
        cfg = MagicMock()
        cfg.timelapse.enable = False
        with self._swap_config(cfg):
            with patch.object(self.svc._jobstore, "remove_job") as mock_remove:
                self.svc.init_timelapse()
        mock_remove.assert_called_once_with(SchedulerSvc.TIMELAPSE_JOB)

    def test_init_timelapse_disabled_job_not_found_logged(self):
        cfg = MagicMock()
        cfg.timelapse.enable = False
        with self._swap_config(cfg):
            with patch.object(self.svc._jobstore, "remove_job",
                              side_effect=JobLookupError(SchedulerSvc.TIMELAPSE_JOB)):
                self.svc.init_timelapse()

    # ------------------------------------------------------------------
    # init_backup_file
    # ------------------------------------------------------------------

    def test_init_backup_file_disabled_removes_job(self):
        cfg = MagicMock()
        cfg.backup.file_enable = False
        with self._swap_config(cfg):
            with patch.object(self.svc._jobstore, "remove_job") as mock_remove:
                self.svc.init_backup_file()
        mock_remove.assert_called_once_with(SchedulerSvc.FILE_BACKUP_JOB)

    def test_init_backup_file_disabled_job_not_found_logged(self):
        cfg = MagicMock()
        cfg.backup.file_enable = False
        with self._swap_config(cfg):
            with patch.object(self.svc._jobstore, "remove_job",
                              side_effect=JobLookupError(SchedulerSvc.FILE_BACKUP_JOB)):
                self.svc.init_backup_file()

    # ------------------------------------------------------------------
    # init_backup_db
    # ------------------------------------------------------------------

    def test_init_backup_db_disabled_removes_job(self):
        cfg = MagicMock()
        cfg.backup.db_enable = False
        with self._swap_config(cfg):
            with patch.object(self.svc._jobstore, "remove_job") as mock_remove:
                self.svc.init_backup_db()
        mock_remove.assert_called_once_with(SchedulerSvc.DB_BACKUP_JOB)

    def test_init_backup_db_disabled_job_not_found_logged(self):
        cfg = MagicMock()
        cfg.backup.db_enable = False
        with self._swap_config(cfg):
            with patch.object(self.svc._jobstore, "remove_job",
                              side_effect=JobLookupError(SchedulerSvc.DB_BACKUP_JOB)):
                self.svc.init_backup_db()

    # ------------------------------------------------------------------
    # init_aqi
    # ------------------------------------------------------------------

    def test_init_aqi_disabled_removes_job(self):
        cfg = MagicMock()
        cfg.aqi.enable = False
        with self._swap_config(cfg):
            with patch.object(self.svc._jobstore, "remove_job") as mock_remove:
                self.svc.init_aqi()
        mock_remove.assert_called_once_with(SchedulerSvc.AQI_JOB)

    def test_init_aqi_disabled_job_not_found_logged(self):
        cfg = MagicMock()
        cfg.aqi.enable = False
        with self._swap_config(cfg):
            with patch.object(self.svc._jobstore, "remove_job",
                              side_effect=JobLookupError(SchedulerSvc.AQI_JOB)):
                self.svc.init_aqi()

    # ------------------------------------------------------------------
    # init_wu
    # ------------------------------------------------------------------

    def test_init_wu_disabled_removes_job(self):
        cfg = MagicMock()
        cfg.wu.enable = False
        with self._swap_config(cfg):
            with patch.object(self.svc._jobstore, "remove_job") as mock_remove:
                self.svc.init_wu()
        mock_remove.assert_called_once_with(SchedulerSvc.WU_JOB)

    def test_init_wu_disabled_job_not_found_logged(self):
        cfg = MagicMock()
        cfg.wu.enable = False
        with self._swap_config(cfg):
            with patch.object(self.svc._jobstore, "remove_job",
                              side_effect=JobLookupError(SchedulerSvc.WU_JOB)):
                self.svc.init_wu()

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
