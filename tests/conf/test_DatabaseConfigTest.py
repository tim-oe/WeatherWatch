import unittest

import pprint

from conf.AppConfig import AppConfig
from conf.DatabaseConfig import DatabaseConfig

class DatabaseConfigTest(unittest.TestCase):
    URL_MATCH = "mariadb\\+mariadbconnector://(.*?):(.*?)@127.0.0.1:3306/weather"

    def test(self):
        ac = AppConfig()

        print(ac.database)
        pprint.pprint(ac.database.__dict__)

        self.assertRegex(str(ac.database.url), DatabaseConfigTest.URL_MATCH)
