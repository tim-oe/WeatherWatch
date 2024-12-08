
from py_singleton import singleton
from conf.AppConfig import AppConfig
from conf.CameraConfig import CameraConfig
from conf.FileBackupConfig import FileBackupConfig
from conf.TimelapseConfig import TimelapseConfig
from util import Rsync
from util.Logger import logger

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

    def camera(self):
        if self._FileBackupConfig.enable:
            rsync: Rsync = Rsync()

            if self._cameraConfig.enable:
                self.logger.info("starting camera backup")
                folder = self._cameraConfig.folder.resolve()
                if folder.endswith("/"):
                    folder = folder.rstrip("/")

                rsync.archive(folder, self._FileBackupConfig.folder)

                if self._FileBackupConfig.purge_enable:            
                    rsync.purge(folder, self._FileBackupConfig.img_old)
                
                self.logger.info("camera backup complete")
            
            if self._timelapseConfig.enable:
                self.logger.info("starting timelapse backup")
                folder = self._timelapseConfig.folder.resolve()
                if folder.endswith("/"):
                    folder = folder.rstrip("/")

                rsync.archive(folder, self._FileBackupConfig.folder)

                if folder.endswith("/"):            
                    rsync.purge(folder, self._FileBackupConfig.img_old)
                self.logger.info("timelapse backup complete")
        
