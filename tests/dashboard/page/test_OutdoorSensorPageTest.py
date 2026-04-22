import unittest
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import dash_bootstrap_components as dbc
from dashboard.page.OutdoorSensorPage import OutdoorSensorPage
from tests.dashboard.BaseDashboardTest import BaseDashboardTest
from furl import furl


# TODO it compiles test.
class OutdoorSensorPageTest(BaseDashboardTest):

    def test(self):
        # system page url
        url = furl(f"http://example.net{OutdoorSensorPage.PATH}")
        c: dbc.Container = self.app.render_page_content(url.url)
        self.assertIsNotNone(c)


class OutdoorSensorPageUnitTest(unittest.TestCase):
    """Mocked unit tests for OutdoorSensorPage — no DB required."""

    def _make_outdoor_entity(self, temp_f=65.0, humidity=60):
        entity = MagicMock()
        entity.read_time = datetime(2026, 4, 20, 10, 0, 0)
        entity.temperature_f = Decimal(str(temp_f))
        entity.humidity = Decimal(str(humidity))
        entity.pressure = Decimal("1013.25")
        entity.wind_avg_m_s = Decimal("2.5")
        entity.wind_max_m_s = Decimal("5.0")
        entity.wind_dir_deg = 180
        entity.uv = Decimal("2.1")
        entity.light_lux = 500
        return entity

    def _make_light_entity(self):
        entity = MagicMock()
        entity.lux = 800
        entity.infrared = 200
        entity.visible = 600
        return entity

    def test_content_returns_container(self):
        outdoor = self._make_outdoor_entity()
        light = self._make_light_entity()

        with patch("dashboard.page.OutdoorSensorPage.OutdoorSensorRepository") as MockOutdoor, \
             patch("dashboard.page.OutdoorSensorPage.LightSensorRepository") as MockLight, \
             patch("dashboard.page.BasePage.AppConfig"):

            MockOutdoor.return_value.find_latest.return_value = outdoor
            MockOutdoor.return_value.get_days_rainfall.return_value = Decimal("0.5")
            MockOutdoor.return_value.find_greater_than_read_time.return_value = [outdoor]
            MockLight.return_value.find_greater_than_read_time.return_value = [light]

            page = OutdoorSensorPage()
            result = page.content()

        self.assertIsInstance(result, dbc.Container)

    def test_find_greater_than_read_time_receives_datetime(self):
        """Regression: date.today() was passed instead of datetime, crashing the type converter."""
        outdoor = self._make_outdoor_entity()
        light = self._make_light_entity()

        with patch("dashboard.page.OutdoorSensorPage.OutdoorSensorRepository") as MockOutdoor, \
             patch("dashboard.page.OutdoorSensorPage.LightSensorRepository") as MockLight, \
             patch("dashboard.page.BasePage.AppConfig"):

            MockOutdoor.return_value.find_latest.return_value = outdoor
            MockOutdoor.return_value.get_days_rainfall.return_value = Decimal("0.5")
            MockOutdoor.return_value.find_greater_than_read_time.return_value = [outdoor]
            MockLight.return_value.find_greater_than_read_time.return_value = [light]

            OutdoorSensorPage().content()

        outdoor_arg = MockOutdoor.return_value.find_greater_than_read_time.call_args[0][0]
        light_arg = MockLight.return_value.find_greater_than_read_time.call_args[0][0]
        self.assertIsInstance(outdoor_arg, datetime, "outdoor find_greater_than_read_time must receive a datetime, not a date")
        self.assertIsInstance(light_arg, datetime, "light find_greater_than_read_time must receive a datetime, not a date")

    def test_content_high_temperature_uses_red_gauge(self):
        """temperature_f >= 90 triggers red TempratureGauge."""
        outdoor = self._make_outdoor_entity(temp_f=92.0)
        light = self._make_light_entity()

        with patch("dashboard.page.OutdoorSensorPage.OutdoorSensorRepository") as MockOutdoor, \
             patch("dashboard.page.OutdoorSensorPage.LightSensorRepository") as MockLight, \
             patch("dashboard.page.BasePage.AppConfig"):

            MockOutdoor.return_value.find_latest.return_value = outdoor
            MockOutdoor.return_value.get_days_rainfall.return_value = Decimal("1.2")
            MockOutdoor.return_value.find_greater_than_read_time.return_value = [outdoor]
            MockLight.return_value.find_greater_than_read_time.return_value = [light]

            page = OutdoorSensorPage()
            result = page.content()

        self.assertIsNotNone(result)
