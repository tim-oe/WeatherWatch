from datetime import datetime
from decimal import Decimal
import unittest
from urllib.parse import urlparse
from unittest.mock import MagicMock, patch

from util.Converter import Converter
from wu.WUClient import WUClient
from wu.WUData import WUData


def _make_data() -> WUData:
    return WUData(
        winddir=180,
        windspeedmph=Decimal('1.2'),
        windgustmph=Decimal('2.3'),
        humidity=55,
        tempf=Decimal('70.72'),
        dailyrainin=Decimal('0.3'),
        baromin=Decimal('29.89'),
        solarradiation=Decimal('1.2'),
        uv=Decimal('1.1'),
        indoortempf=Decimal('68.3'),
        indoorhumidity=40,
        dewptf=Decimal('60.0'))


class WUClientTest(unittest.TestCase):

    def test(self):
        client: WUClient = WUClient()
        data: WUData = _make_data()
        data.aqpm2_5(2)
        data.aqpm10(3)
        print(str(data))
        client.post(datetime.now(), data, end_point=urlparse("http://www.outboundengine.com"))

    def test_dateutc_is_utc(self):
        """dateutc posted to WU must be UTC, not local time."""
        # Use a fixed winter local time (CST = UTC-6)
        local = datetime(2026, 1, 15, 10, 0, 0)
        expected_utc_str = "2026-01-15 16:00:00"

        mock_resp = MagicMock()
        mock_resp.status_code = 200

        with patch("wu.WUClient.requests.get", return_value=mock_resp) as mock_get:
            client: WUClient = WUClient()
            data: WUData = _make_data()
            client.post(local, data)

        self.assertEqual(expected_utc_str, data.dateutc)

    def test_dateutc_cdt(self):
        """dateutc in CDT (UTC-5): local 10:00 -> posted as 15:00 UTC."""
        local = datetime(2026, 7, 15, 10, 0, 0)
        expected_utc_str = "2026-07-15 15:00:00"

        mock_resp = MagicMock()
        mock_resp.status_code = 200

        with patch("wu.WUClient.requests.get", return_value=mock_resp):
            client: WUClient = WUClient()
            data: WUData = _make_data()
            client.post(local, data)

        self.assertEqual(expected_utc_str, data.dateutc)

    def test_non_200_response_raises(self):
        """A non-200 HTTP status from WU should raise RequestException."""
        from requests import RequestException
        mock_resp = MagicMock()
        mock_resp.status_code = 503
        mock_resp.reason = "Service Unavailable"

        with patch("wu.WUClient.requests.get", return_value=mock_resp):
            client = WUClient()
            data = _make_data()
            with self.assertRaises(RequestException):
                client.post(datetime.now(), data)
