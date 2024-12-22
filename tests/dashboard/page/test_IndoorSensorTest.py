
from conf.SensorConfig import SensorConfig
from conf.AppConfig import AppConfig
from dashboard.page.IndoorSensorPage import IndoorSensorPage
from sensor.sdr.IndoorData import IndoorData
from tests.dashboard.BaseDashboardTest import BaseDashboardTest
from furl import furl
import dash_bootstrap_components as dbc
from typing import List

 
# TODO it compiles test.
class AirQualityPageTest(BaseDashboardTest):
    
    def test(self):
        sensors: List[SensorConfig] = AppConfig().sensors
        
        for s in sensors:
            if s.data_class == IndoorData.__name__:
                
                url = furl(f"http://example.net{s.data_class}")
                url.args["name"] = s.name
                    
                c: dbc.Container = self.app.render_page_content(url.url)
                self.assertIsNotNone(c)
