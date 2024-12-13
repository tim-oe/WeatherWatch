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
    https://github.com/litl/backoff
    """

    END_POINT_URL: ParseResult = urlparse("https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php")

    def __init__(self):
        self._wuConfig: WUConfig = AppConfig().wu

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=AppConfig().wu.retries, jitter=None)
    def post(self, readTime: datetime, data: WUData, endPoint: ParseResult = END_POINT_URL):
        data.stationId(self._wuConfig.stationId)
        data.stationKey(self._wuConfig.stationKey)
        data.readTime(Converter.to_utc(readTime))

        resp: requests.Response = requests.get(endPoint.geturl(), params=data.__dict__)
        self.logger.debug("request %s", resp.url)

        if resp.status_code != 200:
            raise RequestException(f"failed to post to weather underground {resp.status_code} {resp.reason}")
