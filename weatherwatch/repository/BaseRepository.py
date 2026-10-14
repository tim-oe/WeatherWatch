import json
import re
from datetime import date, datetime, timezone
from typing import Generic, List, TypeVar, Union

from conf.AppConfig import AppConfig
from repository.DataStore import DataStore
from repository.db_read import db_read, is_connection_error
from spool.EntityCodec import EntityCodec
from spool.SpoolStore import SpoolStore
from sqlalchemy import Connection
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.sql import text
from util.Logger import logger

__all__ = ["BaseRepository"]

T = TypeVar("T")


@logger
class BaseRepository(Generic[T]):
    # pylint: disable=line-too-long
    """
    base repository
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
        self._datastore: DataStore = DataStore()

    @property
    def entity(self) -> DeclarativeBase:
        """
        entity property getter
        :param self: this
        :return: the entity
        """
        return self._entity

    @staticmethod
    def _coerce_to_datetime(dt: Union[date, datetime]) -> datetime:
        """
        Ensure dt is a datetime before it reaches the LocalToUTCDateTime type
        converter, which requires a datetime (not a bare date).

        Callers may pass either a date or a datetime; this normalises both so
        the persistence layer is the only code that needs to be aware of the
        distinction.  A bare date is promoted to midnight of that day.
        """
        if isinstance(dt, datetime):
            return dt
        return datetime(dt.year, dt.month, dt.day)

    def insert(self, o: T):
        """
        insert new object, spooling when the database is unreachable
        :param self: this
        :param o: the object to insert
        """
        if self._spool_enabled() and self._datastore.is_offline():
            self._spool(o)
            return
        session: Session = self._datastore.session
        session.expire_on_commit = False
        try:
            session.add(o)
            session.commit()
            self._datastore.mark_online()
        except Exception as exc:
            self._rollback(session)
            if self._spool_enabled() and is_connection_error(exc):
                if self._datastore.mark_offline():
                    self.logger.warning("database unavailable, spooling writes: %s", exc)
                self._spool(o)
                return
            raise
        finally:
            session.close()

    def insert_direct(self, o: T):
        """
        insert with no spool fallback
        :param self: this
        :param o: the object to insert
        """
        session: Session = self._datastore.session
        session.expire_on_commit = False
        try:
            session.add(o)
            session.commit()
        except Exception:
            self._rollback(session)
            raise
        finally:
            session.close()

    def replay(self, entity: T) -> bool:
        """
        insert a spooled entity; a duplicate key counts as already delivered
        :param self: this
        :param entity: the decoded entity
        :return: True when a new row was inserted
        """
        try:
            self.insert_direct(entity)
            return True
        except IntegrityError:
            self.logger.warning("replay skipped duplicate %s", type(entity).__name__)
            return False

    def spool_decode(self, data: dict) -> T:
        """
        build an entity from an envelope data object
        :param self: this
        :param data: the spooled columns
        :return: the entity
        """
        return EntityCodec.decode(self._entity, data)

    def after_drain(self, first_read_time):
        """
        post-drain hook; subclasses override when a column is derived
        :param self: this
        :param first_read_time: earliest replayed read_time, or None
        """

    def _spool(self, o: T):
        """
        encode the entity and append an envelope for this repository
        :param self: this
        :param o: the object to spool
        """
        payload = {
            "repository": f"{type(self).__module__}.{type(self).__qualname__}",
            "entity": type(o).__name__,
            "spooled_at": datetime.now(timezone.utc).isoformat(),
            "data": EntityCodec.encode(o),
        }
        SpoolStore().append(self._entity.__tablename__, json.dumps(payload))

    def _spool_enabled(self) -> bool:
        """
        whether connection failures are buffered locally
        :param self: this
        :return: the spool enable flag
        """
        return AppConfig().spool.enable

    @staticmethod
    def _rollback(session: Session):
        """
        roll back, ignoring a dead connection
        :param session: the session
        """
        try:
            session.rollback()
        except Exception:
            pass

    @db_read(default=None)
    def find_by_id(self, record_id: int) -> T:
        """
        find record by id
        :param self: this
        :param record_id: the object identity
        :return: the object for the given id
        """
        session: Session = self._datastore.session
        try:
            return session.query(self._entity).filter_by(id=record_id).first()
        finally:
            session.close()

    @db_read(default=[])
    def top(self, limit: int) -> List[T]:
        """
        get top most objects to the limit
        :param self: this
        :param limit: the number of object to get
        :return: list of top objects
        """
        session: Session = self._datastore.session
        try:
            return session.query(self._entity).limit(limit).all()
        finally:
            session.close()

    def delete(self, o: T):
        """
        delete object
        :param self: this
        :param o: the object to delete
        """
        session: Session = self._datastore.session
        try:
            session.delete(o)
            session.commit()
        finally:
            session.close()

    def exec(self, sql: str):
        """
        execute sql statement
        :param self: this
        :param sql: the statement
        """
        con: Connection = self._datastore.connection
        try:
            con.execute(text(sql))
            con.commit()
        finally:
            con.close()

    def exec_file(self, f: str):
        """
        crude sql script processor
        doesn't handle comments
        :param self: this
        :param f: the file
        """
        con: Connection = self._datastore.connection
        try:
            with open(f, "r", encoding="utf-8") as file:
                statements = re.split(r";\s*$", file.read(), flags=re.MULTILINE)
                for statement in statements:
                    if statement:
                        con.execute(text(statement.strip()))

                con.commit()
        finally:
            con.close()
