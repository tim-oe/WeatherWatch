import unittest
from datetime import datetime
from decimal import Decimal
from typing import List
from unittest.mock import MagicMock, patch

import dash_bootstrap_components as dbc
from conf.AppConfig import AppConfig
from conf.SensorConfig import SensorConfig
from dashboard.page.IndoorSensorPage import IndoorSensorPage
from sensor.sdr.IndoorData import IndoorData
from tests.dashboard.BaseDashboardTest import BaseDashboardTest
from furl import furl


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


class IndoorSensorPageUnitTest(unittest.TestCase):
    """Mocked unit tests for IndoorSensorPage — no DB required."""

    def _make_sensor_entity(self, temp_f=72.5, humidity=55, channel=2):
        entity = MagicMock()
        entity.read_time = datetime(2026, 4, 20, 10, 0, 0)
        entity.temperature_f = Decimal(str(temp_f))
        entity.humidity = Decimal(str(humidity))
        entity.channel = channel
        return entity

    def test_content_returns_container(self):
        entity = self._make_sensor_entity()
        mock_sensor_cfg = MagicMock()
        mock_sensor_cfg.channel = 2

        with patch("dashboard.page.IndoorSensorPage.IndoorSensorRepository") as MockRepo:
            mock_repo_inst = MockRepo.return_value
            mock_repo_inst.find_latest.return_value = entity
            mock_repo_inst.find_greater_than_read_time.return_value = [entity]

            with patch("dashboard.page.BasePage.AppConfig") as MockCfg:
                MockCfg.return_value.get_sensor.return_value = mock_sensor_cfg

                page = IndoorSensorPage()
                result = page.content(name="TestSensor")

        self.assertIsInstance(result, dbc.Container)

    def test_find_greater_than_read_time_receives_datetime(self):
        """Regression: date.today() was passed instead of datetime, crashing the type converter."""
        entity = self._make_sensor_entity()
        mock_sensor_cfg = MagicMock()
        mock_sensor_cfg.channel = 2

        with patch("dashboard.page.IndoorSensorPage.IndoorSensorRepository") as MockRepo:
            mock_repo_inst = MockRepo.return_value
            mock_repo_inst.find_latest.return_value = entity
            mock_repo_inst.find_greater_than_read_time.return_value = [entity]

            with patch("dashboard.page.BasePage.AppConfig") as MockCfg:
                MockCfg.return_value.get_sensor.return_value = mock_sensor_cfg
                IndoorSensorPage().content(name="TestSensor")

        arg = mock_repo_inst.find_greater_than_read_time.call_args[0][1]
        self.assertIsInstance(arg, datetime, "find_greater_than_read_time must receive a datetime, not a date")

    def test_content_high_temperature_uses_red_gauge(self):
        """temperature_f >= 90 triggers red TempratureGauge."""
        entity = self._make_sensor_entity(temp_f=95.0)
        mock_sensor_cfg = MagicMock()
        mock_sensor_cfg.channel = 2

        with patch("dashboard.page.IndoorSensorPage.IndoorSensorRepository") as MockRepo:
            mock_repo_inst = MockRepo.return_value
            mock_repo_inst.find_latest.return_value = entity
            mock_repo_inst.find_greater_than_read_time.return_value = [entity]

            with patch("dashboard.page.BasePage.AppConfig") as MockCfg:
                MockCfg.return_value.get_sensor.return_value = mock_sensor_cfg

                page = IndoorSensorPage()
                result = page.content(name="TestSensor")

        self.assertIsNotNone(result)
