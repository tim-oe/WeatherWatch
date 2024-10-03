from conf.AppConfig import AppConfig
from conf.DatabaseConfig import DatabaseConfig
from py_singleton import singleton
from sqlalchemy import Connection, create_engine
from sqlalchemy.orm import Session, sessionmaker

__all__ = ["DataStore"]


@singleton
class DataStore:
    """
    DataStore for orm
    https://medium.com/@danielwume/must-know-package-to-build-your-system-real-world-examples-with-sqlalchemy-in-python-db8c72a0f6c1
    https://docs.sqlalchemy.org/en/20/core/engines.html#creating-urls-programmatically
    TODO pooling https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine
    https://docs.sqlalchemy.org/en/20/core/pooling.html#connection-pool-configuration
    """

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._dbConfig: DatabaseConfig = AppConfig().database

        # https://docs.sqlalchemy.org/en/20/core/pooling.html#using-a-pool-instance-directly
        self._engine = create_engine(self._dbConfig.url, max_overflow=3, pool_size=3, pool_pre_ping=True)

    @property
    def session(self) -> Session:
        """
        session property getter
        :param self: this
        :return: the session
        """
        Session = sessionmaker(bind=self._engine)
        return Session()

    @property
    def connection(self) -> Connection:
        """
        session property getter
        :param self: this
        :return: the session
        """
        return self._engine.connect()
