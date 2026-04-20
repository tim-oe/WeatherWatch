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


@pytest.fixture(scope="session", autouse=True)
def mariadb_container(request):
    """Session-scoped MariaDB testcontainer for @pytest.mark.db tests.

    Skips Docker startup entirely when no db-marked tests are selected (e.g. the
    default unit-test run).  When db tests are present:
      1. Starts a MariaDB 11 container.
      2. Loads timezone tables so migrations that SET TIME_ZONE = 'America/Chicago' work.
      3. Runs all migrations from sql/schema/ via pyway — the single source of truth.
      4. Points AppConfig / DataStore at the container via env vars.
    """
    db_tests = [item for item in request.session.items if item.get_closest_marker("db")]
    if not db_tests:
        yield None
        return

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

        # Load IANA timezone tables so migration files that reference named
        # timezones (e.g. 'America/Chicago') execute without error.
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

        # Run all schema migrations via pyway — no duplicate DDL files needed.
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

        # Inject connection params so AppConfig / DataStore point at the container.
        os.environ["WW_DB_HOST"] = host
        os.environ["WW_DB_PORT"] = str(port)
        os.environ["WW_DB_USERNAME"] = _DB_USER
        os.environ["WW_DB_PASSWORD"] = _DB_PASS
        os.environ["WW_DB_NAME"] = _DB_NAME
        os.environ["WW_DB_DIALECT"] = "mysql"
        os.environ["WW_DB_DRIVER"] = "pymysql"
        os.environ["WW_DB_PROD"] = "false"

        # Reset singletons so the first repository call re-initialises them
        # using the env vars above.
        AppConfig.inst = None
        AppConfig.inited = False
        DataStore.inst = None
        DataStore.inited = False

        yield container

        # Teardown: restore singleton state and remove injected env vars.
        AppConfig.inst = None
        AppConfig.inited = False
        DataStore.inst = None
        DataStore.inited = False
        for key in ("WW_DB_HOST", "WW_DB_PORT", "WW_DB_USERNAME", "WW_DB_PASSWORD",
                    "WW_DB_NAME", "WW_DB_DIALECT", "WW_DB_DRIVER", "WW_DB_PROD"):
            os.environ.pop(key, None)
