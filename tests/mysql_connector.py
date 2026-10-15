"""Import shim for the MySQL Connector/Python C extension."""

import sys
import types


def allow_pure_mysql_connector() -> None:
    """Let pyway import when the MySQL C extension cannot load.

    pyway imports CMySQLConnection even though it connects with the pure-Python
    driver. The x86_64 wheel requires OpenSSL 3.2, and the GitHub Ubuntu 24.04
    runner ships OpenSSL 3.0. A stub satisfies that import.
    """
    try:
        import _mysql_connector  # noqa: F401
    except ImportError:
        sys.modules.pop("_mysql_connector", None)
        stub = types.ModuleType("_mysql_connector")
        stub.MySQLInterfaceError = type("MySQLInterfaceError", (Exception,), {})
        stub.MySQL = type("MySQL", (), {})
        stub.__file__ = __file__
        sys.modules["_mysql_connector"] = stub
