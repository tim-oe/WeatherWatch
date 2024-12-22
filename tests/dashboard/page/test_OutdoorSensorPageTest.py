
from dashboard.page.OutdoorSensorPage import OutdoorSensorPage
from tests.dashboard.BaseDashboardTest import BaseDashboardTest
from furl import furl
import dash_bootstrap_components as dbc
 
# TODO it compiles test.
class OutdoorSensorPageTest(BaseDashboardTest):
    
    def test(self):
        # system page url
        url = furl(f"http://example.net{OutdoorSensorPage.PATH}")
        c: dbc.Container = self.app.render_page_content(url.url)
        self.assertIsNotNone(c)
