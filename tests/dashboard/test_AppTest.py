
from tests.dashboard.BaseDashboardTest import BaseDashboardTest
from furl import furl
import dash_bootstrap_components as dbc
 
# TODO it compiles test.
class AppTest(BaseDashboardTest):
    
    def test(self):
        # unknown page
        url = furl("http://example.net/blah")
        c: dbc.Container = self.app.render_page_content(url.url)
        self.assertIsNotNone(c)

        url = furl("http://example.net/error")
        c: dbc.Container = self.app.server_error(url)
        self.assertIsNotNone(c)

        # TODO not currently working
        # res = self.app.serve_cam_image("current.jpg")
        # self.assertIsNotNone(res)

        # res = self.app.serve_cam_vid("current.mp4")
        # self.assertIsNotNone(res)

        # res = self.app.serve_res_image("error.jpg")
        # self.assertIsNotNone(res)