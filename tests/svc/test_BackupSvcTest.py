from datetime import datetime, timedelta
import os
from pathlib import Path
import shutil
import unittest
import glob

from conf.AppConfig import AppConfig
from conf.CameraConfig import CameraConfig
from conf.FileBackupConfig import FileBackupConfig
from conf.TimelapseConfig import TimelapseConfig
from svc.BackupSvc import BackupSvc

class BackupSvcTest(unittest.TestCase):

    def setup_method(self, test_method):
        self.svc: BackupSvc = BackupSvc()
        self.cc: CameraConfig = AppConfig().camera
        self.fbc: FileBackupConfig = AppConfig().file_backup
        self.tlc: TimelapseConfig = AppConfig().timelapse
        for f in self.fbc.folder.iterdir():
            if(f.is_dir):
                shutil.rmtree(f)
            else:    
                f.unlink()

    def teardown_method(self, test_method):
        for f in self.fbc.folder.iterdir():
            if(f.is_dir):
                shutil.rmtree(f)
            else:
                 f.unlink()
        
    def test_file(self):
        test_dir = Path("tests/data/img")
        cutoff_date = datetime.now() - timedelta(days=self.fbc.img_old + 1)
       
        for f in test_dir.iterdir():
            if(f.is_file):
                shutil.copy(f, self.cc.folder)
                os.utime(f, (cutoff_date.timestamp(), cutoff_date.timestamp()))

        test_dir = Path("tests/data/vids")       
        cutoff_date = datetime.now() - timedelta(days=self.fbc.vid_old + 1)
        for f in test_dir.iterdir():
            if(f.is_file):
                shutil.copy(f, self.tlc.folder)
                os.utime(f, (cutoff_date.timestamp(), cutoff_date.timestamp()))
        
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
