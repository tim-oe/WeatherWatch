import unittest

from src.conf.AppConfig import AppConfig
from src.conf.DatabaseConfig import DatabaseConfig

class DatabaseConfigTest(unittest.TestCase):
    URL_MATCH = "mysql\+mysqlconnector://(.*?):(.*?)@localhost:3306/weather"

    def test(self):
        ac = AppConfig()
        self.assertRegex(ac.database.url, DatabaseConfigTest.URL_MATCH)
