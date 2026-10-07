import os
import re
import subprocess
from pathlib import Path

from conf.AppConfig import AppConfig
from conf.BackupConfig import BackupConfig
from conf.CameraConfig import CameraConfig
from conf.TimelapseConfig import TimelapseConfig
from py_singleton import singleton
from util.Emailer import Emailer
from util.Logger import logger
from util.Rsync import Rsync

__all__ = ["BackupSvc", "mount_fstype"]

_NFS_TYPES = ("nfs", "nfs4")
_MOUNT_ESCAPE = re.compile(r"\\([0-7]{3})")


def _unescape_mount(value: str) -> str:
    """
    undo octal escapes used in /proc/self/mountinfo paths
    :param value: the raw mount field
    :return: the unescaped path
    """
    return _MOUNT_ESCAPE.sub(lambda match: chr(int(match.group(1), 8)), value)


def _mount_covers(mountpoint: str, resolved: str) -> bool:
    """
    whether resolved sits on mountpoint
    :param mountpoint: the mount point
    :param resolved: the absolute path being checked
    :return: True when resolved is the mount or a child of it
    """
    if mountpoint == "/":
        return resolved.startswith("/")
    prefix = mountpoint.rstrip("/")
    return resolved == prefix or resolved.startswith(prefix + "/")


def mount_fstype(resolved: str, mountinfo: str) -> str | None:
    """
    longest mount-point prefix of resolved, read from mountinfo text
    :param resolved: absolute path
    :param mountinfo: contents of /proc/self/mountinfo
    :return: fstype, or None when no mount covers the path
    """
    best_len = -1
    best_fs = None
    for line in mountinfo.splitlines():
        parts = line.split()
        if "-" not in parts:
            continue
        separator = parts.index("-")
        if separator < 5 or separator + 1 >= len(parts):
            continue
        mountpoint = _unescape_mount(parts[4])
        fstype = parts[separator + 1]
        if _mount_covers(mountpoint, resolved) and len(mountpoint) > best_len:
            best_len = len(mountpoint)
            best_fs = fstype
    return best_fs


def _absolute_path(path: Path) -> Path:
    """Return an absolute lexical path without touching the filesystem."""
    return Path(os.path.abspath(os.path.expanduser(str(path))))


@logger
@singleton
class BackupSvc:
    """
    system backup service
    performs camera and timelapse backup
    """

    MOUNTINFO = "/proc/self/mountinfo"
    PROBE_TIMEOUT = 10

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._camera_config: CameraConfig = AppConfig().camera
        self._timelapse_config: TimelapseConfig = AppConfig().timelapse
        self._backup_config: BackupConfig = AppConfig().backup
        self._rsync: Rsync = Rsync()
        self._dest_alerted = False

        self._base_dir: Path = self._backup_config.folder

    def camera(self):
        """
        backup camera resource files
        :param self: this
        """
        if not self._backup_config.file_enable:
            return
        if not self._dest_ready(self._backup_config.folder):
            return
        backup_folder = str(_absolute_path(self._backup_config.folder))
        self.backup_stills(backup_folder)
        self.backup_vids(backup_folder)

    def backup_stills(self, backup_folder):
        """
        backup camera image
        :param self: this
        :param backup_folder: archive destination
        """
        if self._camera_config.enable:
            self.logger.info("starting camera backup")
            folder = str(self._camera_config.folder.resolve())
            if folder.endswith("/"):
                folder = folder.rstrip("/")

            if self._rsync.archive(folder, backup_folder) and self._backup_config.purge_enable:
                self._rsync.purge(folder, self._backup_config.img_old)
            elif self._backup_config.purge_enable:
                self.logger.error("camera archive failed; skipping purge")

            self.logger.info("camera backup complete")

    def backup_vids(self, backup_folder):
        """
        backup timelapse video
        :param self: this
        :param backup_folder: archive destination
        """
        if self._timelapse_config.enable:
            self.logger.info("starting timelapse backup")
            folder = str(self._timelapse_config.folder.resolve())
            if folder.endswith("/"):
                folder = folder.rstrip("/")

            if self._rsync.archive(folder, backup_folder) and self._backup_config.purge_enable:
                self._rsync.purge(folder, self._backup_config.vid_old)
            elif self._backup_config.purge_enable:
                self.logger.error("timelapse archive failed; skipping purge")
            self.logger.info("timelapse backup complete")

    def _dest_ready(self, folder: Path) -> bool:
        """
        destination is a writable nfs mount, unless require_mount is off
        :param self: this
        :param folder: configured backup folder
        :return: True when archive and purge may run
        """
        resolved = _absolute_path(folder)
        if self._backup_config.require_mount:
            mountinfo = Path(self.MOUNTINFO).read_text(encoding="utf-8")
            fstype = mount_fstype(str(resolved), mountinfo)
            if fstype not in _NFS_TYPES:
                shown = fstype if fstype is not None else "unmounted"
                self._alert_dest(f"backup folder '{folder}' resolved to '{resolved}' on '{shown}', expected nfs")
                return False
        if not self._probe_writable(resolved):
            self._alert_dest(f"backup folder '{folder}' resolved to '{resolved}' is not writable")
            return False
        self._dest_alerted = False
        return True

    def _probe_writable(self, folder: Path) -> bool:
        """
        touch and unlink a probe file in a killable subprocess
        :param self: this
        :param folder: directory to probe
        :return: True when both steps finish in time
        """
        probe = str(folder / ".ww-backup-probe")
        try:
            created = subprocess.run(
                ["mkdir", "-p", str(folder)],
                timeout=self.PROBE_TIMEOUT,
                check=False,
            )
            if created.returncode != 0:
                return False
            touched = subprocess.run(["touch", probe], timeout=self.PROBE_TIMEOUT, check=False)
            if touched.returncode != 0:
                return False
            removed = subprocess.run(["unlink", probe], timeout=self.PROBE_TIMEOUT, check=False)
            return removed.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except OSError:
            return False

    def _alert_dest(self, message: str):
        """
        log and email once per failure streak
        :param self: this
        :param message: the failure detail
        """
        self.logger.error(message)
        if self._dest_alerted:
            return
        self._dest_alerted = True
        Emailer().send_alert("Camera backup destination not ready", message)
