from datetime import datetime
from urllib.parse import ParseResult, urlparse

import backoff
import requests
from conf.AppConfig import AppConfig
from conf.WUConfig import WUConfig
from py_singleton import singleton
from requests import RequestException
from util.Converter import Converter
from util.Logger import logger
from wu.WUData import WUData

__all__ = ["WUClient"]


@logger
@singleton
class WUClient:
    """
    post data to weather underground
    https://support.weather.com/s/article/PWS-Upload-Protocol?language=en_US
    https://docs.google.com/document/d/1eKCnKXI9xnoMGRRzOL1xPCBihNV2rOet08qpE_gArAY/edit?pli=1&tab=t.0
    https://requests.readthedocs.io/en/latest/user/quickstart/
    https://requests.readthedocs.io/en/latest/user/advanced/#timeouts
    https://github.com/litl/backoff
    """

    END_POINT_URL: ParseResult = urlparse("https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php")

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._wu_config: WUConfig = AppConfig().wu

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=AppConfig().wu.retries, jitter=None)
    def post(self, read_time: datetime, data: WUData, end_point: ParseResult = END_POINT_URL):
        """
        post data to weather underground
        will backoff and retry n times based on config
        :param self: this
        :param read_time: data read time
        :param data: sensors data
        :param end_point: the end_point url
        """
        data.station_id(self._wu_config.station_id)
        data.station_key(self._wu_config.station_key)
        data.read_time(Converter.to_utc(read_time))

        resp: requests.Response = requests.get(end_point.geturl(), params=data.__dict__, timeout=30)
        self.logger.debug("request %s", resp.url)

        if resp.status_code != 200:
            raise RequestException(f"failed to post to weather underground {resp.status_code} {resp.reason}")
