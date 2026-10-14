from functools import wraps

from repository.DataStore import DataStore
from sqlalchemy.exc import DBAPIError, InterfaceError, OperationalError

__all__ = ["db_read", "is_connection_error"]


def is_connection_error(exc: BaseException) -> bool:
    """
    connection-class database errors that should spool or degrade
    :param exc: the raised error
    :return: True for an unreachable database
    """
    if isinstance(exc, (OperationalError, InterfaceError)):
        return True
    if isinstance(exc, DBAPIError) and bool(getattr(exc, "connection_invalidated", False)):
        return True
    return False


def _fresh(default):
    """
    copy mutable defaults so callers do not share one list
    :param default: the decorator default
    :return: a per-call value
    """
    if isinstance(default, list):
        return list(default)
    return default


def db_read(default=None):
    """
    return default when the database is offline or a connection error is raised
    :param default: value returned instead of propagating
    :return: the method decorator
    """

    def decorate(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            store = DataStore()
            if store.is_offline():
                self.logger.warning("skipping %s; database offline", method.__name__)
                return _fresh(default)
            try:
                return method(self, *args, **kwargs)
            except Exception as exc:
                if not is_connection_error(exc):
                    raise
                store.mark_offline()
                self.logger.warning("%s failed; database unavailable", method.__name__)
                return _fresh(default)

        return wrapper

    return decorate
