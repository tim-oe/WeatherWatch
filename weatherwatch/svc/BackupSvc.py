import concurrent
import functools
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path

from backup.BackupRange import BackupRange
from conf.AppConfig import AppConfig
from conf.BackupConfig import BackupConfig
from conf.CameraConfig import CameraConfig
from conf.TimelapseConfig import TimelapseConfig
from py_singleton import singleton
from repository.AQISensorRepository import AQISensorRepository
from repository.IndoorSensorRepository import IndoorSensorRepository
from repository.OutdoorSensorRepository import OutdoorSensorRepository
from util.Logger import logger
from util.Rsync import Rsync

__all__ = ["BackupSvc"]


@logger
@singleton
class BackupSvc:

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._cameraConfig: CameraConfig = AppConfig().camera
        self._timelapseConfig: TimelapseConfig = AppConfig().timelapse
        self._backupConfig: BackupConfig = AppConfig().backup

        # run db backups concurrently
        self._backup_pool = ThreadPoolExecutor(max_workers=3)
        self._rsync: Rsync = Rsync()

        self._baseDir: Path = self._backupConfig.folder
        self._baseDir.mkdir(parents=True, exist_ok=True)

        self._db_m_dir: Path = Path(self._baseDir / "db/m")
        self._db_m_dir.mkdir(parents=True, exist_ok=True)
        self._db_w_dir: Path = Path(self._baseDir / "db/w")
        self._db_w_dir.mkdir(parents=True, exist_ok=True)

    def camera(self):
        if self._backupConfig.file_enable:
            backup_folder = str(self._backupConfig.folder.resolve())
            if self._cameraConfig.enable:
                self.logger.info("starting camera backup")
                folder = str(self._cameraConfig.folder.resolve())
                if folder.endswith("/"):
                    folder = folder.rstrip("/")

                self._rsync.archive(folder, backup_folder)

                if self._backupConfig.purge_enable:
                    self._rsync.purge(folder, self._backupConfig.img_old)

                self.logger.info("camera backup complete")

            if self._timelapseConfig.enable:
                self.logger.info("starting timelapse backup")
                folder = str(self._timelapseConfig.folder.resolve())
                if folder.endswith("/"):
                    folder = folder.rstrip("/")

                self._rsync.archive(folder, backup_folder)

                if self._backupConfig.purge_enable:
                    self._rsync.purge(folder, self._backupConfig.vid_old)
                self.logger.info("timelapse backup complete")

    def db(self):
        if self._backupConfig.db_enable:
            active_threads = set()
            active_threads.add(self._backup_pool.submit(functools.partial(self.outdoor_sensor_backup)))
            active_threads.add(self._backup_pool.submit(functools.partial(self.indoor_sensor_backup)))
            active_threads.add(self._backup_pool.submit(functools.partial(self.aqi_sensor_backup)))

            future: Future
            for future in concurrent.futures.as_completed(active_threads):
                self.logger.info("thread complete %s", future.result)

    def outdoor_sensor_backup(self):
        self.db_backup(OutdoorSensorRepository())

    def indoor_sensor_backup(self):
        self.db_backup(IndoorSensorRepository())

    def aqi_sensor_backup(self):
        self.db_backup(AQISensorRepository())

    def db_backup(self, repo):
        self.logger.info("backup %s", repo.entity.__table__)
        try:
            m: BackupRange = BackupRange.prev_month()
            w: BackupRange = BackupRange.prev_week()

            mf: Path = Path(self._db_m_dir / f"{m.file_prefix}_{repo.entity.__table__}.sql")
            wf: Path = Path(self._db_w_dir / f"{w.file_prefix}_{repo.entity.__table__}.sql")

            if not mf.is_file():
                self.logger.info("peforming monthly backup of %s %s %s", m.from_date, m.to_date, repo.entity.__table__)
                repo.backup(m.from_date, m.to_date, mf)
                self._rsync.purge(self._db_w_dir, self._backupConfig.db_weekly_old)
            else:
                self.logger.info("skiping backup of %s", mf)

            if not wf.is_file():
                self.logger.info("peforming weekly backup of %s %s %s", w.from_date, w.to_date, repo.entity.__table__)
                repo.backup(w.from_date, w.to_date, wf)
            else:
                self.logger.info("skiping backup of %s", wf)

        except Exception:
            self.logger.exception("error performing backup for %s", repo.entity.__table__)
