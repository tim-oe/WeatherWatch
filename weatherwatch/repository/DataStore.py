import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from conf.AppConfig import AppConfig
from conf.DatabaseConfig import DatabaseConfig
from py_singleton import singleton
from python_event_bus import EventBus
from sqlalchemy import Connection, Engine, create_engine, text
from sqlalchemy.orm import Session
from util.Logger import logger

__all__ = ["DataStore"]


@logger
@singleton
class DataStore:
    """
    DataStore for orm
    https://medium.com/@danielwume/must-know-package-to-build-your-system-real-world-examples-with-sqlalchemy-in-python-db8c72a0f6c1
    https://docs.sqlalchemy.org/en/20/core/engines.html#creating-urls-programmatically
    https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine
    https://docs.sqlalchemy.org/en/20/core/pooling.html#connection-pool-configuration
    """

    ONLINE_EVENT = "DataStoreOnline"
    CONNECT_TIMEOUT = 5
    READ_TIMEOUT = 10
    WRITE_TIMEOUT = 10
    POOL_RECYCLE_SECONDS = 3600
    OFFLINE_RETRY_SECONDS = 60

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._db_config: DatabaseConfig = AppConfig().database
        self._state_lock = threading.Lock()
        self._offline_until: datetime | None = None
        self._online_pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="datastore-online")

        # https://docs.sqlalchemy.org/en/20/core/pooling.html#using-a-pool-instance-directly
        self._engine: Engine = create_engine(
            self._db_config.url,
            pool_size=self._db_config.pool_size,
            max_overflow=self._db_config.pool_overflow,
            pool_pre_ping=True,
            pool_recycle=DataStore.POOL_RECYCLE_SECONDS,
            connect_args={
                "connect_timeout": DataStore.CONNECT_TIMEOUT,
                "read_timeout": DataStore.READ_TIMEOUT,
                "write_timeout": DataStore.WRITE_TIMEOUT,
            },
        )

    @property
    def session(self) -> Session:
        """
        session property getter
        :param self: this
        :return: the session
        """
        return Session(self._engine)

    @property
    def connection(self) -> Connection:
        """
        connection property getter
        :param self: this
        :return: the connection
        """
        return self._engine.connect()

    def is_available(self) -> bool:
        """
        probe the database with SELECT 1
        :param self: this
        :return: True when the probe succeeds
        """
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def is_offline(self) -> bool:
        """
        whether writes should skip the database until the retry window passes
        :param self: this
        :return: True inside the offline window
        """
        with self._state_lock:
            if self._offline_until is None:
                return False
            until = self._offline_until
            if until.tzinfo is None:
                until = until.replace(tzinfo=timezone.utc)
            return datetime.now(timezone.utc) < until

    def mark_offline(self) -> bool:
        """
        start or extend the offline retry window
        :param self: this
        :return: True when this call entered the window
        """
        with self._state_lock:
            now = datetime.now(timezone.utc)
            already = self._offline_until is not None and now < self._offline_until
            self._offline_until = now + timedelta(seconds=DataStore.OFFLINE_RETRY_SECONDS)
            return not already

    def mark_online(self):
        """
        clear the offline window and emit DataStoreOnline on that transition
        :param self: this
        """
        fire = False
        with self._state_lock:
            if self._offline_until is not None:
                self._offline_until = None
                fire = True
        if fire:
            self._online_pool.submit(self._emit_online)

    def _emit_online(self):
        """
        dispatch the online event off the caller thread
        :param self: this
        """
        EventBus.call(DataStore.ONLINE_EVENT)
