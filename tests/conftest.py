import os

import pytest
from pyway.configfile import ConfigFile
from pyway.migrate import Migrate
from testcontainers.mysql import MySqlContainer

from conf.AppConfig import AppConfig
from repository.DataStore import DataStore

_DB_NAME = "weather"
_DB_USER = "weather"
_DB_PASS = "weather"
_DB_ROOT_PASS = "weather"
_MIGRATION_DIR = "sql/schema"
_PYWAY_TABLE = "pyway"

_INJECTED_ENV = (
    "WW_DB_HOST",
    "WW_DB_PORT",
    "WW_PORT",
    "WW_DB_USERNAME",
    "WW_DB_PASSWORD",
    "WW_DB_NAME",
    "WW_DB_DIALECT",
    "WW_DB_DRIVER",
    "WW_DB_PROD",
)


@pytest.fixture(scope="session", autouse=True)
def mariadb_container():
    """Session-scoped MariaDB testcontainer for the whole pytest run.

    Every test that talks to MariaDB (repository, dashboard sample load,
    CameraSvc, WuSvc, backups, integration) must hit this container, not
    the host weather database. Docker is required for pytest.
    """
    with MySqlContainer(
        image="mariadb:11",
        dialect="pymysql",
        username=_DB_USER,
        password=_DB_PASS,
        root_password=_DB_ROOT_PASS,
        dbname=_DB_NAME,
    ) as container:
        host = container.get_container_host_ip()
        port = container.get_exposed_port(3306)

        tz_result = container.exec(
            ["bash", "-c",
             f"mariadb-tzinfo-to-sql /usr/share/zoneinfo "
             f"| mariadb -u root -p{_DB_ROOT_PASS} mysql "
             f"&& mariadb -u root -p{_DB_ROOT_PASS} -e 'FLUSH TABLES;'"]
        )
        assert tz_result.exit_code == 0, (
            f"Timezone table load failed (exit {tz_result.exit_code}): "
            f"{tz_result.output.decode()}"
        )

        cfg = ConfigFile()
        cfg.database_type = "mysql"
        cfg.database_host = host
        cfg.database_port = str(port)
        cfg.database_name = _DB_NAME
        cfg.database_username = _DB_USER
        cfg.database_password = _DB_PASS
        cfg.database_migration_dir = _MIGRATION_DIR
        cfg.database_table = _PYWAY_TABLE
        Migrate(cfg).run()

        os.environ["WW_DB_HOST"] = host
        os.environ["WW_DB_PORT"] = str(port)
        # weatherwatch.yml reads port from WW_PORT, not WW_DB_PORT
        os.environ["WW_PORT"] = str(port)
        os.environ["WW_DB_USERNAME"] = _DB_USER
        os.environ["WW_DB_PASSWORD"] = _DB_PASS
        os.environ["WW_DB_NAME"] = _DB_NAME
        os.environ["WW_DB_DIALECT"] = "mysql"
        os.environ["WW_DB_DRIVER"] = "pymysql"
        os.environ["WW_DB_PROD"] = "false"

        AppConfig.inst = None
        AppConfig.inited = False
        DataStore.inst = None
        DataStore.inited = False

        yield container

        AppConfig.inst = None
        AppConfig.inited = False
        DataStore.inst = None
        DataStore.inited = False
        for key in _INJECTED_ENV:
            os.environ.pop(key, None)
