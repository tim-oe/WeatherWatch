import importlib
import json
import threading

from py_singleton import singleton
from python_event_bus import EventBus
from repository.DataStore import DataStore
from repository.db_read import is_connection_error
from spool.SpoolStore import SpoolStore
from util.Logger import logger

__all__ = ["DBFlushSvc"]


@logger
@singleton
class DBFlushSvc:
    """
    replay spooled rows once the database is reachable
    """

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._lock = threading.Lock()
        self._store = SpoolStore()
        self._datastore = DataStore()
        EventBus.subscribe(DataStore.ONLINE_EVENT, self.process)

    def process(self, *_args, **_kwargs):
        """
        drain every spooled table
        :param self: this
        """
        # non-blocking: a waiting `with` would queue a second drain behind the first
        if not self._lock.acquire(blocking=False):  # pylint: disable=consider-using-with
            self.logger.info("db flush already running")
            return
        try:
            self._drain()
        finally:
            self._lock.release()

    def _drain(self):
        """
        health-check, then replay oldest segment first
        :param self: this
        """
        if not self._datastore.is_available():
            return
        self._datastore.mark_online()
        for table in self._store.tables():
            repo, failed, replayed, duplicates, rejected = self._drain_table(table)
            if not failed:
                try:
                    self._finish_table(table, repo)
                except Exception as exc:
                    failed = True
                    if is_connection_error(exc):
                        self._datastore.mark_offline()
                    self.logger.exception("db flush after_drain failed for table %s", table)
            # an empty directory is checked every interval; only a pass that moved rows is info
            log = self.logger.info if failed or replayed or duplicates or rejected else self.logger.debug
            log(
                "db flush table=%s replayed=%s duplicates=%s rejected=%s failed=%s",
                table,
                replayed,
                duplicates,
                rejected,
                failed,
            )
        self._store.reset_alerts_if_empty()

    def _drain_table(self, table: str):
        """
        replay one table's segments
        :param self: this
        :param table: the table directory name
        :return: repo, failed, replayed, duplicates, rejected
        """
        repo = None
        replayed = 0
        duplicates = 0
        rejected = 0
        while True:
            path = self._store.claim_oldest(table)
            if path is None:
                return repo, False, replayed, duplicates, rejected
            lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
            outcome = self._replay_lines(table, lines)
            repo = outcome["repo"] or repo
            replayed += outcome["replayed"]
            duplicates += outcome["duplicates"]
            rejected += outcome["rejected"]
            if outcome["failed"]:
                self._store.rewrite(path, outcome["remaining"])
                return repo, True, replayed, duplicates, rejected
            self._store.complete(path)

    def _replay_lines(self, table: str, lines: list[str]) -> dict:
        """
        replay lines until a connection failure
        :param self: this
        :param table: the table directory name
        :param lines: envelope lines
        :return: counters and any remainder
        """
        outcome = {"repo": None, "replayed": 0, "duplicates": 0, "rejected": 0, "failed": False, "remaining": []}
        for index, line in enumerate(lines):
            try:
                envelope = json.loads(line)
            except json.JSONDecodeError:
                self._store.quarantine(table, line, "invalid json")
                outcome["rejected"] += 1
                continue
            repo, reason = self._resolve(table, envelope)
            if repo is None:
                self._store.quarantine(table, line, reason)
                outcome["rejected"] += 1
                continue
            outcome["repo"] = repo
            try:
                entity = repo.spool_decode(envelope.get("data") or {})
                if repo.replay(entity):
                    outcome["replayed"] += 1
                else:
                    outcome["duplicates"] += 1
                read_time = getattr(entity, "read_time", None)
                if read_time is not None:
                    self._store.remember_read_time(table, envelope.get("repository", ""), read_time)
            except Exception as exc:
                if is_connection_error(exc):
                    self._datastore.mark_offline()
                    self.logger.warning("replay failed; database unavailable: %s", exc)
                    outcome["failed"] = True
                    outcome["remaining"] = lines[index:]
                    return outcome
                self._store.quarantine(table, line, str(exc))
                outcome["rejected"] += 1
        return outcome

    def _finish_table(self, table: str, repo):
        """
        run after_drain once the table has no segments left
        :param self: this
        :param table: the table directory name
        :param repo: the repository that owned the rows, if any
        """
        start, dotted = self._store.peek_window(table)
        if repo is None and dotted:
            repo, _reason = self._resolve(table, {"repository": dotted, "entity": None, "data": {}})
        if repo is None:
            return
        repo.after_drain(start)
        self._store.clear_window(table)

    def _resolve(self, table: str, envelope: dict):
        """
        import the repository named by the envelope
        :param self: this
        :param table: the directory the line was read from
        :param envelope: the spooled envelope
        :return: repository instance and a rejection reason
        """
        dotted = envelope.get("repository", "")
        if not isinstance(dotted, str) or not dotted.startswith("repository.") or ".." in dotted.split("."):
            return None, "repository path rejected"
        module_name, _, qualname = dotted.rpartition(".")
        if not module_name.startswith("repository."):
            return None, "repository path rejected"
        try:
            module = importlib.import_module(module_name)
            obj = module
            for part in qualname.split("."):
                obj = getattr(obj, part)
            repo = obj()
        except Exception as exc:
            return None, f"repository import failed: {exc}"
        entity = getattr(repo, "entity", None)
        tablename = getattr(entity, "__tablename__", None)
        if tablename != table:
            return None, f"tablename {tablename} does not match {table}"
        expected = envelope.get("entity")
        if expected is not None and expected != entity.__name__:
            return None, f"entity {expected} does not match {entity.__name__}"
        return repo, None
