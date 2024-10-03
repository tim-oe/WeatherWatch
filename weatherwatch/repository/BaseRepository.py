from typing import Generic, List, TypeVar

from repository.DataStore import DataStore
from sqlalchemy import Connection
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

__all__ = ["BaseRepository"]

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    DataStore for orm
    https://github.com/auth0-blog/sqlalchemy-orm-tutorial
    https://medium.com/@danielwume/must-know-package-to-build-your-system-real-world-examples-with-sqlalchemy-in-python-db8c72a0f6c1
    https://docs.sqlalchemy.org/en/20/dialects/mysql.html#module-sqlalchemy.dialects.mysql.mariadbconnector
    """

    def __init__(self, entity):
        """
        ctor
        :param self: this
        """
        self._entity = entity
        self._datastore: DataStore = DataStore()

    def insert(self, o: T):
        try:
            session: Session = self._datastore.session
            session.add(o)
            session.commit()
            session.refresh(o)
        finally:
            session.close()

    def findById(self, id: int) -> T:
        try:
            session: Session = self._datastore.session
            return session.query(self._entity).filter_by(id=id).first()
        finally:
            session.close()

    def top(self, limit: int) -> List[T]:
        try:
            session: Session = self._datastore.session
            return session.query(self._entity).limit(limit).all()
        finally:
            session.close()

    def delete(self, o: T):
        try:
            session: Session = self._datastore.session
            session.delete(o)
            session.commit()
        finally:
            session.close()

    def exec(self, sql: str):
        try:
            con: Connection = self._datastore.connection

            con.execute(text(sql))
            con.commit()
        finally:
            con.close()
