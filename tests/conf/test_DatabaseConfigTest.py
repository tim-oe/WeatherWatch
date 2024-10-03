import unittest

from weatherwatch.conf.AppConfig import AppConfig
from weatherwatch.conf.DatabaseConfig import DatabaseConfig

class DatabaseConfigTest(unittest.TestCase):
    URL_MATCH = "mariadb\\+mariadbconnector://(.*?):(.*?)@127.0.0.1:3306/weather"

    def test(self):
        ac = AppConfig()
        self.assertRegex(str(ac.database.url), DatabaseConfigTest.URL_MATCH)
