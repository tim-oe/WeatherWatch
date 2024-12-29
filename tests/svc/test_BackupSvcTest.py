from datetime import datetime, timedelta
import os
from pathlib import Path
import shutil
import unittest
import glob

from backup.BackupRange import BackupRange
from camera.Camera import Camera
from camera.Timelapse import Timelapse
from conf.AppConfig import AppConfig
from conf.CameraConfig import CameraConfig
from conf.BackupConfig import BackupConfig
from conf.TimelapseConfig import TimelapseConfig
from svc.BackupSvc import BackupSvc
from tests.repository.BaseRepositoryTest import BaseRespositoryTest

class BackupSvcTest(unittest.TestCase):

    def setup_method(self, test_method):
        print(f"test setup {test_method}")
            
        self.svc: BackupSvc = BackupSvc()

        self.cc: CameraConfig = AppConfig().camera
        self.tlc: TimelapseConfig = AppConfig().timelapse
        self.fbc: BackupConfig = AppConfig().backup
        # init folders
        self.camera: Camera = Camera()
        self.timelapse: Timelapse = Timelapse()
        
        self.purge()

    def teardown_method(self, test_method):
       self.purge()
        
    def purge(self):
        for f in self.fbc.folder.iterdir():
            if(f.is_dir):
                for f2 in f.iterdir():
                    if(f2.is_file()):
                        f2.unlink()
            else:    
                f.unlink()

        dir: Path = Path(self.fbc.folder / "db/m")
        for f in dir.iterdir():
                f.unlink()

        dir: Path = Path(self.fbc.folder / "db/w")
        for f in dir.iterdir():
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

    def test_db_month(self):
        dir: Path = Path(self.fbc.folder / "db/m")

        w: BackupRange = BackupRange.prev_month()

        BaseRespositoryTest.load(w.from_date + timedelta(days=8))
        
        self.svc.db()

        self.assertLess(0, len(glob.glob(str(dir / '*.zip'))))

        for f in dir.iterdir():
            self.assertTrue(f.is_file())
            self.assertLess(0, f.stat().st_size)

    def test_db_week(self):
        dir: Path = Path(self.fbc.folder / "db/w")

        w: BackupRange = BackupRange.prev_week()

        BaseRespositoryTest.load(w.from_date + timedelta(days=8))
        
        self.svc.db()

        self.assertLess(0, len(glob.glob(str(dir / '*'))))

        for f in dir.iterdir():
            self.assertTrue(f.is_file())
            self.assertLess(0, f.stat().st_size)


