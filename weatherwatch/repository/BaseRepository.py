import json
import re
from typing import Generic, List, TypeVar

from conf.AppConfig import AppConfig
from conf.DatabaseConfig import DatabaseConfig
from repository.DataStore import DataStore
from sqlalchemy import Column, Connection, DateTime, Integer, Numeric, Table, insert
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.sql import text
from util.Logger import logger

__all__ = ["BaseRepository"]

T = TypeVar("T")


@logger
class BaseRepository(Generic[T]):
    """
    DataStore for orm
    https://github.com/auth0-blog/sqlalchemy-orm-tutorial
    https://medium.com/@danielwume/must-know-package-to-build-your-system-real-world-examples-with-sqlalchemy-in-python-db8c72a0f6c1
    https://docs.sqlalchemy.org/en/20/dialects/mysql.html#module-sqlalchemy.dialects.mysql.mariadbconnector
    TODO: https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
    https://transaction.readthedocs.io/en/latest/sqlalchemy.html
    """  # noqa

    def __init__(self, entity):
        """
        ctor
        :param self: this
        """
        self._entity = entity
        self._config: DatabaseConfig = AppConfig().database
        self._datastore: DataStore = DataStore()
        self._table: Table = self._datastore.get_table_def(self._entity.__tablename__)

        self._columns = {}
        c: Column

        for c in self._table.columns:
            self._columns[c.name] = c.type

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

    def execFile(self, f: str):
        """
        crude sql script processor
        doesn't handle comments
        """
        con: Connection = self._datastore.connection
        try:
            with open(f) as file:
                statements = re.split(r";\s*$", file.read(), flags=re.MULTILINE)
                for statement in statements:
                    if statement:
                        con.execute(text(statement.strip()))

                con.commit()
        finally:
            con.close()

    def get_insert(self, o: T) -> str:

        raw = o.__dict__.copy()
        del raw["_sa_instance_state"]

        insert_stmt = insert(self._table).values(raw)
        sql: str = str(insert_stmt)
        for key, value in raw.items():
            sql = sql.replace(f":{key}", self.get_value(key, value))

        return sql

    def get_value(self, key: str, value) -> str:
        t = self._columns[key]

        self.logger.debug("%s %s %s", key, type(t), value)

        # getting mysql specific type for bool
        if isinstance(value, bool):
            if value:
                return "1"
            else:
                return "0"
        # needs to be valid json
        elif key == "raw":
            return f"'{json.dumps(value)}'"
        else:
            match t:
                case DateTime():
                    # TODO is there more generic way
                    dt = value.strftime("%Y-%m-%d %H:%M:%S")
                    return f"'{dt}'"
                case Numeric() | Integer():
                    return str(value)
                case _:
                    # value = str(value)
                    value = value.replace("'", "''")
                    return f"'{value}'"
