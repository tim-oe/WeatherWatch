from sqlalchemy import Connection, create_engine
from sqlalchemy.orm import Session, sessionmaker

from conf.AppConfig import AppConfig
from conf.DatabaseConfig import DatabaseConfig

__all__ = ["DataStore"]


class DataStore(object):
    """
    DataStore for orm
    https://medium.com/@danielwume/must-know-package-to-build-your-system-real-world-examples-with-sqlalchemy-in-python-db8c72a0f6c1
    """

    # override for singleton
    # https://www.geeksforgeeks.org/singleton-pattern-in-python-a-complete-guide/
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(DataStore, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._dbConfig: DatabaseConfig = AppConfig().database
        self._engine = create_engine(self._dbConfig.url)

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
