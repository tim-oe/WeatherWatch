import os
import unittest
import pprint
from unittest.mock import patch

from conf.AppConfig import AppConfig
from conf.DatabaseConfig import DatabaseConfig


class DatabaseConfigTest(unittest.TestCase):
    URL_MATCH = "mariadb\\+mariadbconnector://(.*?):(.*?)@127.0.0.1:3306/weather"

    def test(self):
        ac = AppConfig()

        print(ac.database)
        pprint.pprint(ac.database.__dict__)

        self.assertRegex(str(ac.database.url), DatabaseConfigTest.URL_MATCH)

    def test_pool_properties(self):
        ac = AppConfig()
        db = ac.database
        self.assertGreater(db.pool_size, 0)
        self.assertGreater(db.pool_overflow, 0)
        self.assertIsNotNone(db.production)

    def test_missing_env_vars_raises(self):
        """Omitting env vars should raise an Exception during construction."""
        ac = AppConfig()
        raw_cfg = dict(ac.database.__dict__)
        raw_cfg.pop("logger", None)
        raw_cfg.pop("backup_enable", None)
        raw_cfg.pop("backup_folder", None)

        config_dict = {
            DatabaseConfig.DIALECT_KEY: raw_cfg.get(DatabaseConfig.DIALECT_KEY, "mariadb"),
            DatabaseConfig.DRIVER_KEY: raw_cfg.get(DatabaseConfig.DRIVER_KEY, "mariadbconnector"),
            DatabaseConfig.HOST_KEY: raw_cfg.get(DatabaseConfig.HOST_KEY, "127.0.0.1"),
            DatabaseConfig.PORT_KEY: raw_cfg.get(DatabaseConfig.PORT_KEY, 3306),
            DatabaseConfig.NAME_KEY: raw_cfg.get(DatabaseConfig.NAME_KEY, "weather"),
            DatabaseConfig.PRODUCTION_KEY: False,
            DatabaseConfig.POOL_KEY: {DatabaseConfig.SIZE_KEY: 5, DatabaseConfig.OVERFLOW_KEY: 10},
            DatabaseConfig.BACKUP_KEY: {DatabaseConfig.ENABLE_KEY: False, DatabaseConfig.FOLDER_KEY: "/tmp"},
        }
        env_without_db = {k: v for k, v in os.environ.items()
                          if k not in (DatabaseConfig.USERNAME_ENVAR, DatabaseConfig.PASSWORD_ENVAR)}
        with patch.dict("os.environ", env_without_db, clear=True):
            with self.assertRaises(Exception):
                DatabaseConfig(config_dict)

    def test_backup_properties(self):
        """backup_enable and backup_folder properties when backup section is present."""
        config_dict = {
            DatabaseConfig.DIALECT_KEY: "mariadb",
            DatabaseConfig.DRIVER_KEY: "mariadbconnector",
            DatabaseConfig.HOST_KEY: "127.0.0.1",
            DatabaseConfig.PORT_KEY: 3306,
            DatabaseConfig.NAME_KEY: "weather",
            DatabaseConfig.USERNAME_KEY: "testuser",
            DatabaseConfig.PASSWORD_KEY: "testpass",
            DatabaseConfig.PRODUCTION_KEY: False,
            DatabaseConfig.POOL_KEY: {DatabaseConfig.SIZE_KEY: 5, DatabaseConfig.OVERFLOW_KEY: 10},
            DatabaseConfig.BACKUP_KEY: {DatabaseConfig.ENABLE_KEY: True, DatabaseConfig.FOLDER_KEY: "/tmp/backup"},
        }
        with patch.dict("os.environ", {
            DatabaseConfig.USERNAME_ENVAR: "testuser",
            DatabaseConfig.PASSWORD_ENVAR: "testpass",
        }):
            db = DatabaseConfig(config_dict)
            self.assertTrue(db.backup_enable)
            self.assertEqual("/tmp/backup", db.backup_folder)
