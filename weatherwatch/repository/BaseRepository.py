from typing import Generic, List, TypeVar

from repository.DataStore import DataStore
from sqlalchemy import Connection
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.sql import text

__all__ = ["BaseRepository"]

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    DataStore for orm
    https://github.com/auth0-blog/sqlalchemy-orm-tutorial
    https://medium.com/@danielwume/must-know-package-to-build-your-system-real-world-examples-with-sqlalchemy-in-python-db8c72a0f6c1
    https://docs.sqlalchemy.org/en/20/dialects/mysql.html#module-sqlalchemy.dialects.mysql.mariadbconnector
    TODO: https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
    """  # noqa

    def __init__(self, entity):
        """
        ctor
        :param self: this
        """
        self._entity = entity
        self._datastore: DataStore = DataStore()

    @property
    def entity(self) -> DeclarativeBase:
        """
        entity property getter
        :param self: this
        :return: the entity
        """
        return self._entity

    def insert(self, o: T):
        session: Session = self._datastore.session
        try:
            session.add(o)
            session.commit()
            session.refresh(o)
        finally:
            session.close()

    def findById(self, id: int) -> T:
        session: Session = self._datastore.session
        try:
            return session.query(self._entity).filter_by(id=id).first()
        finally:
            session.close()

    def top(self, limit: int) -> List[T]:
        session: Session = self._datastore.session
        try:
            return session.query(self._entity).limit(limit).all()
        finally:
            session.close()

    def delete(self, o: T):
        session: Session = self._datastore.session
        try:
            session.delete(o)
            session.commit()
        finally:
            session.close()

    def exec(self, sql: str):
        con: Connection = self._datastore.connection
        try:
            con.execute(text(sql))
            con.commit()
        finally:
            con.close()
