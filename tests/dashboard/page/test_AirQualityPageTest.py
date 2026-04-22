import unittest
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import dash_bootstrap_components as dbc
from dashboard.page.AirQualityPage import AirQualityPage
from tests.dashboard.BaseDashboardTest import BaseDashboardTest
from furl import furl


# TODO it compiles test.
class AirQualityPageTest(BaseDashboardTest):

    def test(self):
        # system page url
        url = furl(f"http://example.net{AirQualityPage.PATH}")
        c: dbc.Container = self.app.render_page_content(url.url)
        self.assertIsNotNone(c)


class AirQualityPageUnitTest(unittest.TestCase):
    """Mocked unit tests for AirQualityPage — no DB required."""

    def _make_aqi_entity(self):
        entity = MagicMock()
        entity.read_time = datetime(2026, 4, 20, 10, 0, 0)
        entity.pm_1_0_conctrt_atmosph = 5
        entity.pm_2_5_conctrt_atmosph = 10
        entity.pm_10_conctrt_atmosph = 15
        entity.pm_1_0_conctrt_std = 4
        entity.pm_2_5_conctrt_std = 9
        entity.pm_10_conctrt_std = 14
        return entity

    def test_content_returns_container(self):
        entity = self._make_aqi_entity()

        with patch("dashboard.page.AirQualityPage.AQISensorRepository") as MockRepo, \
             patch("dashboard.page.BasePage.AppConfig"):

            MockRepo.return_value.find_latest.return_value = entity
            MockRepo.return_value.find_greater_than_read_time.return_value = [entity]

            page = AirQualityPage()
            result = page.content()

        self.assertIsInstance(result, dbc.Container)

    def test_find_greater_than_read_time_receives_datetime(self):
        """Regression: date.today() was passed instead of datetime, crashing the type converter."""
        entity = self._make_aqi_entity()

        with patch("dashboard.page.AirQualityPage.AQISensorRepository") as MockRepo, \
             patch("dashboard.page.BasePage.AppConfig"):

            MockRepo.return_value.find_latest.return_value = entity
            MockRepo.return_value.find_greater_than_read_time.return_value = [entity]

            AirQualityPage().content()

        arg = MockRepo.return_value.find_greater_than_read_time.call_args[0][0]
        self.assertIsInstance(arg, datetime, "find_greater_than_read_time must receive a datetime, not a date")
