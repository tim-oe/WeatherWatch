
from pathlib import Path
import shutil
from camera.Camera import Camera
from dashboard.page.CameraPage import CameraPage
from tests.dashboard.BaseDashboardTest import BaseDashboardTest
from furl import furl
import dash_bootstrap_components as dbc

from conf.AppConfig import AppConfig
from conf.CameraConfig import CameraConfig
 
# TODO it compiles test.
class CameraPageTest(BaseDashboardTest):
    
    def setup_method(self, method):
        super().setup_method(method)
        
        self.cc: CameraConfig = AppConfig().camera
        # init folders
        self.camera: Camera = Camera()

        test_dir = Path("tests/data/img")
        self.assertTrue(self.cc.folder.is_dir())

        for f in test_dir.iterdir():
            print(f.absolute())
            if(f.is_file):
                print(f"copy img {f.absolute()}")
                shutil.copy(f, self.cc.folder)
           
    def test(self):
        # system page url
        url = furl(f"http://example.net{CameraPage.PATH}")
        c: dbc.Container = self.app.render_page_content(url.url)
        self.assertIsNotNone(c)
