import functools
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from backup.BackupRange import BackupRange
from conf.AppConfig import AppConfig
from conf.BackupConfig import BackupConfig
from conf.CameraConfig import CameraConfig
from conf.TimelapseConfig import TimelapseConfig
from py_singleton import singleton
from repository import OutdoorSensorRepository
from repository.AQISensorRepository import AQISensorRepository
from repository.IndoorSensorRepository import IndoorSensorRepository
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

        self._baseDir: Path = self._backupConfig.folder
        self._baseDir.mkdir(parents=True, exist_ok=True)

        self._db_m_dir: Path = Path(self._baseDir / "db/m")
        self._db_m_dir.mkdir(parents=True, exist_ok=True)
        self._db_w_dir: Path = Path(self._baseDir / "db/w")
        self._db_w_dir.mkdir(parents=True, exist_ok=True)

    def camera(self):
        if self._backupConfig.file_enable:
            rsync: Rsync = Rsync()
            backup_folder = str(self._backupConfig.folder.resolve())
            if self._cameraConfig.enable:
                self.logger.info("starting camera backup")
                folder = str(self._cameraConfig.folder.resolve())
                if folder.endswith("/"):
                    folder = folder.rstrip("/")

                rsync.archive(folder, backup_folder)

                if self._backupConfig.purge_enable:
                    rsync.purge(folder, self._backupConfig.img_old)

                self.logger.info("camera backup complete")

            if self._timelapseConfig.enable:
                self.logger.info("starting timelapse backup")
                folder = str(self._timelapseConfig.folder.resolve())
                if folder.endswith("/"):
                    folder = folder.rstrip("/")

                rsync.archive(folder, backup_folder)

                if self._backupConfig.purge_enable:
                    rsync.purge(folder, self._backupConfig.vid_old)
                self.logger.info("timelapse backup complete")

    def db(self):
        if self._backupConfig.db_enable:
            self._backup_pool.submit(functools.partial(self.outdoor_sensor_backup, self))
            self._backup_pool.submit(functools.partial(self.indoor_sensor_backup, self))
            self._backup_pool.submit(functools.partial(self.aqi_sensor_backup, self))

    def outdoor_sensor_backup(self):
        self.db_backup(OutdoorSensorRepository())

    def indoor_sensor_backup(self):
        self.db_backup(IndoorSensorRepository())

    def aqi_sensor_backup(self):
        self.db_backup(AQISensorRepository())

    def db_backup(self, repo):
        try:
            m: BackupRange = BackupRange.prev_month()
            w: BackupRange = BackupRange.prev_week()

            mf: Path = Path(self._db_m_dir / f"{m.file_prefix}_{repo.entity.__table__}.sql")
            wf: Path = Path(self._db_w_dir / f"{w.file_prefix}_{repo.entity.__table__}.sql")

            if not mf.is_file():
                logger.info("peforming monthly backup of %s", repo.entity.__table__)
                repo.backup(m.to_date, m.from_date, mf)
                # TODO delete the previous months weekly backups

            if not wf.is_file():
                logger.info("peforming weekly backup of %s", repo.entity.__table__)
                repo.backup(w.to_date, w.from_date, wf)
        except Exception:
            self.logger.exception("error performing backup for %s", repo.entity.__table__)
