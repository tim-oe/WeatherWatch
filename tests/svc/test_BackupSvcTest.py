from datetime import datetime, timedelta
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import glob
from unittest.mock import patch

from camera.Camera import Camera
from camera.Timelapse import Timelapse
from conf.AppConfig import AppConfig
from conf.CameraConfig import CameraConfig
from conf.BackupConfig import BackupConfig
from conf.TimelapseConfig import TimelapseConfig
from svc.BackupSvc import BackupSvc, mount_fstype

class BackupSvcTest(unittest.TestCase):

    def setup_method(self, test_method):
        print(f"test setup {test_method}")
            
        self.svc: BackupSvc = BackupSvc()

        self.cc: CameraConfig = AppConfig().camera
        self.tlc: TimelapseConfig = AppConfig().timelapse
        self.fbc: BackupConfig = AppConfig().backup
        self.fbc.folder.mkdir(parents=True, exist_ok=True)
        # init folders
        self.camera: Camera = Camera()
        self.timelapse: Timelapse = Timelapse()
        
        self.purge()

    def teardown_method(self, test_method):
       self.purge()
        
    def purge(self):
        for f in self.fbc.folder.iterdir():
            if f.is_dir():
                for f2 in f.iterdir():
                    if f2.is_file():
                        f2.unlink()
            elif f.is_file():
                f.unlink()

    def setup_files(self, offset: int):
        test_dir = Path("tests/data/img")
        cutoff_date = datetime.now() - timedelta(days=self.fbc.img_old + offset)
        diff_dayz = (datetime.now() - cutoff_date).days
        print(f"is older {(cutoff_date < datetime.now())}")
        print(f"img diff [{diff_dayz}] old [{self.fbc.img_old}]")
        print(f"img now {datetime.now()} then {cutoff_date}")
       
        self.assertTrue(self.cc.folder.is_dir())

        for f in test_dir.iterdir():
            print(f.absolute())
            if(f.is_file):
                print(f"copy img {f.absolute()}")
                shutil.copy(f, self.cc.folder)

        for f in self.cc.folder.iterdir():
            if(f.is_file):
                os.utime(f, (cutoff_date.timestamp(), cutoff_date.timestamp()))

        test_dir = Path("tests/data/vids")       
        cutoff_date = datetime.now() - timedelta(days=self.fbc.vid_old + offset)
        diff_dayz = (datetime.now() - cutoff_date).days
        print(f"is older {(cutoff_date < datetime.now())}")
        print(f"img diff [{diff_dayz}] old [{self.fbc.vid_old}]")
        print(f"vid now {datetime.now()} then {cutoff_date}")

        for f in test_dir.iterdir():
            if(f.is_file):
                print(f"copy vid {f.absolute()}")
                shutil.copy(f, self.tlc.folder)

        for f in self.tlc.folder.iterdir():
            if(f.is_file):
                os.utime(f, (cutoff_date.timestamp(), cutoff_date.timestamp()))

    def test_file_purge(self):
        self.setup_files(1)
                
        self.svc.camera()
        
        found_img: bool = False
        img_dir = Path(self.fbc.folder / self.cc.folder.name)       
                
        for f in img_dir.iterdir():
            if(f.is_file):
                found_img = True
                break
    
        self.assertTrue(found_img)       
        
        self.assertEqual(0, len(glob.glob(str(self.cc.folder / '*'))))
        
        found_vid: bool = False
        vid_dir = Path(self.fbc.folder / self.tlc.folder.name)       
                
        for f in vid_dir.iterdir():
            if(f.is_file):
                found_vid = True
                break
    
        self.assertTrue(found_vid)               
        
        self.assertEqual(0, len(glob.glob(str(self.tlc.folder / '*'))))


    def test_file_no_purge(self):
        self.setup_files(-1)
                
        self.svc.camera()
                    
        self.assertLess(0, len(glob.glob(str(self.cc.folder / '*'))))
                
        self.assertLess(0, len(glob.glob(str(self.tlc.folder / '*'))))


class BackupSvcGateTest(unittest.TestCase):

    def setUp(self):
        self.svc = BackupSvc()
        self.folder = self.svc._backup_config.folder
        self.folder.mkdir(parents=True, exist_ok=True)
        self._require = self.svc._backup_config.require_mount
        self.svc._dest_alerted = False

    def tearDown(self):
        self.svc._backup_config.__dict__["require_mount"] = self._require
        self.svc._dest_alerted = False

    def _mountinfo(self, text: str) -> str:
        handle, name = tempfile.mkstemp(prefix="ww-mountinfo-")
        os.close(handle)
        path = Path(name)
        path.write_text(text, encoding="utf-8")
        self.addCleanup(path.unlink, missing_ok=True)
        return str(path)

    def test_not_mounted_skips_archive(self):
        self.svc._backup_config.__dict__["require_mount"] = True
        mount = self._mountinfo("")
        with patch.object(BackupSvc, "MOUNTINFO", mount), patch.object(self.svc._rsync, "archive") as archive, patch(
            "svc.BackupSvc.Emailer"
        ) as emailer:
            self.svc.camera()
            self.svc.camera()
        archive.assert_not_called()
        emailer.return_value.send_alert.assert_called_once()
        self.assertIn("unmounted", emailer.return_value.send_alert.call_args.args[1])

    def test_wrong_fstype_skips_archive(self):
        self.svc._backup_config.__dict__["require_mount"] = True
        mount = self._mountinfo("1 0 8:1 / / rw - ext4 /dev/root rw\n")
        with patch.object(BackupSvc, "MOUNTINFO", mount), patch.object(self.svc._rsync, "archive") as archive:
            ready = self.svc._dest_ready(self.folder)
        self.assertFalse(ready)
        archive.assert_not_called()

    def test_longest_mount_prefix_wins_without_resolving_path(self):
        mountinfo = "\n".join(
            [
                "1 0 8:1 / / rw - ext4 /dev/root rw",
                "2 1 0:1 / /mnt/backup rw - nfs server:/backup rw",
            ]
        )
        self.assertEqual("nfs", mount_fstype("/mnt/backup/weather", mountinfo))
        self.svc._backup_config.__dict__["require_mount"] = True
        mount = self._mountinfo(mountinfo)
        ok = subprocess.CompletedProcess(args=["probe"], returncode=0)
        with patch.object(BackupSvc, "MOUNTINFO", mount), patch.object(
            Path, "resolve", side_effect=AssertionError("filesystem resolution used")
        ), patch("svc.BackupSvc.subprocess.run", return_value=ok):
            self.assertTrue(self.svc._dest_ready(Path("/mnt/backup/weather")))

    def test_probe_timeout_skips_archive(self):
        self.svc._backup_config.__dict__["require_mount"] = True
        mount = self._mountinfo("1 0 0:1 / / rw - nfs server:/export rw\n")

        def timed_out(*_args, **_kwargs):
            raise subprocess.TimeoutExpired(cmd="touch", timeout=10)

        with patch.object(BackupSvc, "MOUNTINFO", mount), patch("svc.BackupSvc.subprocess.run", side_effect=timed_out):
            self.assertFalse(self.svc._dest_ready(self.folder))

    def test_not_writable_skips_archive(self):
        self.svc._backup_config.__dict__["require_mount"] = True
        mount = self._mountinfo("1 0 0:1 / / rw - nfs server:/export rw\n")
        failed = subprocess.CompletedProcess(args=["touch"], returncode=1)
        with patch.object(BackupSvc, "MOUNTINFO", mount), patch("svc.BackupSvc.subprocess.run", return_value=failed):
            self.assertFalse(self.svc._dest_ready(self.folder))

    def test_require_mount_false_bypasses_fstype(self):
        self.svc._backup_config.__dict__["require_mount"] = False
        mount = self._mountinfo("1 0 8:1 / / rw - ext4 /dev/root rw\n")
        ok = subprocess.CompletedProcess(args=["touch"], returncode=0)
        with patch.object(BackupSvc, "MOUNTINFO", mount), patch("svc.BackupSvc.subprocess.run", return_value=ok), patch.object(
            self.svc._rsync, "archive", return_value=True
        ) as archive, patch.object(self.svc._rsync, "purge"):
            self.svc.camera()
        archive.assert_called()

    def test_probe_creates_directory_in_timeout_protected_subprocess(self):
        self.svc._backup_config.__dict__["require_mount"] = False
        ok = subprocess.CompletedProcess(args=["probe"], returncode=0)
        with patch("svc.BackupSvc.subprocess.run", return_value=ok) as run:
            self.assertTrue(self.svc._probe_writable(Path("/unreachable/backup")))
        self.assertEqual(["mkdir", "-p", "/unreachable/backup"], run.call_args_list[0].args[0])
        self.assertEqual(["touch", "/unreachable/backup/.ww-backup-probe"], run.call_args_list[1].args[0])
        self.assertEqual(["unlink", "/unreachable/backup/.ww-backup-probe"], run.call_args_list[2].args[0])

    def test_archive_failure_skips_purge(self):
        self.svc._backup_config.__dict__["require_mount"] = False
        ok = subprocess.CompletedProcess(args=["touch"], returncode=0)
        with patch("svc.BackupSvc.subprocess.run", return_value=ok), patch.object(
            self.svc._rsync, "archive", return_value=False
        ), patch.object(self.svc._rsync, "purge") as purge:
            self.svc.camera()
        purge.assert_not_called()


