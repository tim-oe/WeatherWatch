from pathlib import Path

from conf.AppConfig import AppConfig
from conf.CameraConfig import CameraConfig
from conf.FileBackupConfig import FileBackupConfig
from conf.TimelapseConfig import TimelapseConfig
from py_singleton import singleton
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
        self._FileBackupConfig: FileBackupConfig = AppConfig().file_backup

        self._baseDir: Path = self._FileBackupConfig.folder

        self._baseDir.mkdir(parents=True, exist_ok=True)

    def camera(self):
        if self._FileBackupConfig.enable:
            rsync: Rsync = Rsync()
            backup_folder = str(self._FileBackupConfig.folder.resolve())
            if self._cameraConfig.enable:
                self.logger.info("starting camera backup")
                folder = str(self._cameraConfig.folder.resolve())
                if folder.endswith("/"):
                    folder = folder.rstrip("/")

                rsync.archive(folder, backup_folder)

                if self._FileBackupConfig.purge_enable:
                    rsync.purge(folder, self._FileBackupConfig.img_old)

                self.logger.info("camera backup complete")

            if self._timelapseConfig.enable:
                self.logger.info("starting timelapse backup")
                folder = str(self._timelapseConfig.folder.resolve())
                if folder.endswith("/"):
                    folder = folder.rstrip("/")

                rsync.archive(folder, backup_folder)

                if self._FileBackupConfig.purge_enable:
                    rsync.purge(folder, self._FileBackupConfig.vid_old)
                self.logger.info("timelapse backup complete")
