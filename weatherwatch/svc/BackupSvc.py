import concurrent
import functools
import glob
import zipfile
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
    """
    system backup service
    performs db and camera backup
    """

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._camera_config: CameraConfig = AppConfig().camera
        self._timelapse_config: TimelapseConfig = AppConfig().timelapse
        self._backup_config: BackupConfig = AppConfig().backup

        # run db backups concurrently
        self._backup_pool = ThreadPoolExecutor(max_workers=3)
        self._rsync: Rsync = Rsync()

        self._base_dir: Path = self._backup_config.folder
        self._base_dir.mkdir(parents=True, exist_ok=True)

        self._db_m_dir: Path = Path(self._base_dir / "db/m")
        self._db_m_dir.mkdir(parents=True, exist_ok=True)
        self._db_w_dir: Path = Path(self._base_dir / "db/w")
        self._db_w_dir.mkdir(parents=True, exist_ok=True)

    def camera(self):
        """
        backup camera resource files
        :param self: this
        """
        if self._backup_config.file_enable:
            backup_folder = str(self._backup_config.folder.resolve())
            self.backup_stills(backup_folder)
            self.backup_vids(backup_folder)

    def backup_stills(self, backup_folder):
        """
        backup camera image
        :param self: this
        """
        if self._camera_config.enable:
            self.logger.info("starting camera backup")
            folder = str(self._camera_config.folder.resolve())
            if folder.endswith("/"):
                folder = folder.rstrip("/")

            self._rsync.archive(folder, backup_folder)

            if self._backup_config.purge_enable:
                self._rsync.purge(folder, self._backup_config.img_old)

            self.logger.info("camera backup complete")

    def backup_vids(self, backup_folder):
        """
        backup camera image
        :param self: this
        """
        if self._timelapse_config.enable:
            self.logger.info("starting timelapse backup")
            folder = str(self._timelapse_config.folder.resolve())
            if folder.endswith("/"):
                folder = folder.rstrip("/")

            self._rsync.archive(folder, backup_folder)

            if self._backup_config.purge_enable:
                self._rsync.purge(folder, self._backup_config.vid_old)
            self.logger.info("timelapse backup complete")

    def db(self):
        """
        main entry point for db backup
        :param self: this
        """
        if self._backup_config.db_enable:
            m: BackupRange = BackupRange.prev_month()

            mf: Path = Path(self._db_m_dir / f"{m.file_prefix}.bz2.zip")

            active_threads = set()
            active_threads.add(self._backup_pool.submit(functools.partial(self.outdoor_sensor_backup, mf)))
            active_threads.add(self._backup_pool.submit(functools.partial(self.indoor_sensor_backup, mf)))
            active_threads.add(self._backup_pool.submit(functools.partial(self.aqi_sensor_backup, mf)))

            future: Future
            for future in concurrent.futures.as_completed(active_threads):
                self.logger.info("thread complete %s", future.result)

            self.archive_monthly(mf)

    def outdoor_sensor_backup(self, monthly_archive):
        """
        backup database outdoor sensor tables
        :param self: this
        :param monthly_archive: the monthly archive file
        """
        self.db_backup(OutdoorSensorRepository(), monthly_archive)

    def indoor_sensor_backup(self, monthly_archive):
        """
        backup database indoor sensor tables
        :param self: this
        :param monthly_archive: the monthly archive file
        """
        self.db_backup(IndoorSensorRepository(), monthly_archive)

    def aqi_sensor_backup(self, monthly_archive):
        """
        backup database aqi sensor tables
        :param self: this
        :param monthly_archive: the monthly archive file
        """
        self.db_backup(AQISensorRepository(), monthly_archive)

    def db_backup(self, repo, monthly_archive):
        """
        backup database table
        performs monthly and weekly backup
        pruning weeklys whe monthy is in place
        :param self: this
        :param repo: the db repo for backup
        :param monthly_archive: the monthly archive file
        """
        self.logger.info("backup %s", repo.entity.__table__)
        try:
            m: BackupRange = BackupRange.prev_month()
            w: BackupRange = BackupRange.prev_week()

            mf: Path = Path(self._db_m_dir / f"{m.file_prefix}_{repo.entity.__table__}.sql")
            wf: Path = Path(self._db_w_dir / f"{w.file_prefix}_{repo.entity.__table__}.sql")

            if not monthly_archive.is_file():
                self.logger.info("peforming monthly backup of %s %s %s", m.from_date, m.to_date, mf.absolute())
                repo.backup(m.from_date, m.to_date, mf)
                self._rsync.purge(self._db_w_dir, self._backup_config.db_weekly_old)
            else:
                self.logger.info("skiping backup of %s", mf)

            # TODO edge case when prev week is in the prev month
            if not wf.is_file():
                self.logger.info("peforming weekly backup of %s %s %s", w.from_date, w.to_date, wf.absolute())
                repo.backup(w.from_date, w.to_date, wf)
            else:
                self.logger.info("skiping backup of %s", wf)

        except Exception:
            self.logger.exception("error performing backup for %s", repo.entity.__table__)

    def archive_monthly(self, mf):
        """
        archive monthly files if created
        performs monthly and weekly backup
        pruning weeklys whe monthy is in place
        :param self: this
        :param mf: the monthly archive file
        """
        self.logger.info("archive monthly files")
        try:
            m: BackupRange = BackupRange.prev_month()

            pattern = f"{m.file_prefix}*.sql"

            if not mf.is_file() and len(glob.glob(str(self._db_m_dir / pattern))) > 2:
                self.logger.info("creating archive %s", mf.absolute())

                with zipfile.ZipFile(mf.resolve(), "w", zipfile.ZIP_BZIP2, compresslevel=9) as archive:
                    for file in self._db_m_dir.glob(pattern):
                        archive.write(file.absolute(), file.name)

                # delete files now in archive
                for file in self._db_m_dir.glob(pattern):
                    self.logger.info("deleting %s", file.absolute())
                    file.unlink()

            else:
                self.logger.info("skiping ar chive %s", mf.absolute())

        except Exception:
            self.logger.exception("error performing monthly archive")
