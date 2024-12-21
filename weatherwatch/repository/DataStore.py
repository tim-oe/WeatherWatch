from conf.AppConfig import AppConfig
from conf.DatabaseConfig import DatabaseConfig
from py_singleton import singleton
from sqlalchemy import Connection, Engine, MetaData, Table, create_engine
from sqlalchemy.orm import Session, sessionmaker

__all__ = ["DataStore"]


@singleton
class DataStore:
    """
    DataStore for orm
    https://medium.com/@danielwume/must-know-package-to-build-your-system-real-world-examples-with-sqlalchemy-in-python-db8c72a0f6c1
    https://docs.sqlalchemy.org/en/20/core/engines.html#creating-urls-programmatically
    https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine
    https://docs.sqlalchemy.org/en/20/core/pooling.html#connection-pool-configuration
    """

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._dbConfig: DatabaseConfig = AppConfig().database

        # https://docs.sqlalchemy.org/en/20/core/pooling.html#using-a-pool-instance-directly
        self._engine: Engine = create_engine(
            self._dbConfig.url,
            max_overflow=self._dbConfig.pool_size,
            pool_size=self._dbConfig.pool_overflow,
            pool_pre_ping=True,
        )

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
        connection property getter
        :param self: this
        :return: the connection
        """
        return self._engine.connect()

    def get_table_def(self, table_name: str) -> Table:
        """
        get tje table metadata definition
        :param self: this
        :param table_name: the table to lookup
        :return: table metadata
        """

        metadata = MetaData()
        metadata.reflect(self._engine)

        return Table(table_name, metadata, autoload_with=self._engine)
