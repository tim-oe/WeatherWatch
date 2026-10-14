import json
import os
import re
import shutil
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

from conf.AppConfig import AppConfig
from py_singleton import singleton
from util.Emailer import Emailer
from util.Logger import logger

__all__ = ["SpoolCapacityError", "SpoolStore"]

_SEGMENT_RE = re.compile(r"^\d{8}T\d{2}\.jsonl$")
_WINDOW_NAME = ".window_start"


class SpoolCapacityError(OSError):
    """The configured free-space floor cannot be preserved."""


@logger
@singleton
class SpoolStore:
    """
    hourly JSON-lines spool, one directory per table
    """

    def __init__(self):
        """
        ctor
        :param self: this
        """
        config = AppConfig().spool
        self._folder = Path(config.folder)
        self._min_free_pct = config.min_free_pct
        self._warn_age_hours = config.warn_age_hours
        self._locks: dict[str, threading.Lock] = {}
        self._locks_guard = threading.Lock()
        self._capacity_lock = threading.Lock()
        self._evict_alerted = False
        self._age_alerted = False
        self._folder.mkdir(parents=True, exist_ok=True)

    def append(self, table: str, line: str):
        """
        append one envelope line to the active hourly segment
        :param self: this
        :param table: the table directory name
        :param line: the JSON envelope without requiring a newline
        """
        segment_name = self._segment_name()
        with self._capacity_lock:
            self._evict_until_fit(segment_name)
            self._warn_if_old()
            directory = self._folder / table
            directory.mkdir(parents=True, exist_ok=True)
            path = directory / segment_name
            with self._lock(table):
                self._write_line(path, line)

    def segments(self, table: str) -> list[Path]:
        """
        hourly segments oldest first, excluding draining and rejected files
        :param self: this
        :param table: the table directory name
        :return: segment paths
        """
        directory = self._folder / table
        if not directory.is_dir():
            return []
        found = [path for path in directory.iterdir() if _SEGMENT_RE.match(path.name)]
        return sorted(found, key=lambda path: path.name)

    def tables(self) -> list[str]:
        """
        table directories present on disk
        :param self: this
        :return: directory names
        """
        if not self._folder.is_dir():
            return []
        return sorted(path.name for path in self._folder.iterdir() if path.is_dir())

    def claim_oldest(self, table: str) -> Path | None:
        """
        rename the oldest segment to .draining, or adopt one left by a crash
        :param self: this
        :param table: the table directory name
        :return: the draining path, or None when the table is empty
        """
        directory = self._folder / table
        if not directory.is_dir():
            return None
        with self._lock(table):
            draining = sorted(directory.glob("*.jsonl.draining"), key=lambda path: path.name)
            if draining:
                return draining[0]
            pending = self.segments(table)
            if not pending:
                return None
            oldest = pending[0]
            dest = oldest.with_name(oldest.name + ".draining")
            oldest.rename(dest)
            return dest

    def release(self, path: Path) -> Path:
        """
        rename a draining file back to its segment name
        :param self: this
        :param path: the draining path
        :return: the restored segment path
        """
        table = path.parent.name
        with self._lock(table):
            if path.name.endswith(".draining"):
                restored = path.with_name(path.name[: -len(".draining")])
                path.rename(restored)
                return restored
            return path

    def complete(self, path: Path):
        """
        delete a draining file after every line committed
        :param self: this
        :param path: the draining path
        """
        table = path.parent.name
        with self._lock(table):
            path.unlink(missing_ok=True)

    def rewrite(self, path: Path, lines: list[str]):
        """
        replace a draining file with the lines still to replay
        :param self: this
        :param path: the draining path
        :param lines: remaining envelope lines
        """
        table = path.parent.name
        temporary = path.parent / (path.name + ".tmp")
        with self._lock(table):
            with temporary.open("w", encoding="utf-8") as handle:
                for line in lines:
                    handle.write(line if line.endswith("\n") else line + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)

    def quarantine(self, table: str, line: str, reason: str):
        """
        append a rejected line
        :param self: this
        :param table: the table directory name
        :param line: the original envelope line
        :param reason: why it was rejected
        """
        directory = self._folder / table
        directory.mkdir(parents=True, exist_ok=True)
        payload = json.dumps({"reason": reason, "line": line})
        with self._lock(table):
            self._write_line(directory / "rejected.jsonl", payload)

    def remember_read_time(self, table: str, repository: str, read_time: datetime):
        """
        keep the earliest replayed read_time so a partial drain can finish later
        :param self: this
        :param table: the table directory name
        :param repository: dotted repository path
        :param read_time: the entity read_time
        """
        directory = self._folder / table
        path = directory / _WINDOW_NAME
        temporary = directory / (_WINDOW_NAME + ".tmp")
        with self._lock(table):
            current, saved_repo = self._read_window(path)
            if current is not None and current <= read_time:
                return
            body = {"repository": saved_repo or repository, "read_time": read_time.isoformat()}
            with temporary.open("w", encoding="utf-8") as handle:
                handle.write(json.dumps(body))
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
            directory_fd = os.open(directory, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)

    def peek_window(self, table: str) -> tuple[datetime | None, str | None]:
        """
        read the stored replay window without removing it
        :param self: this
        :param table: the table directory name
        :return: read_time and repository path
        """
        path = self._folder / table / _WINDOW_NAME
        with self._lock(table):
            return self._read_window(path)

    def clear_window(self, table: str):
        """
        drop the replay window after after_drain runs
        :param self: this
        :param table: the table directory name
        """
        path = self._folder / table / _WINDOW_NAME
        with self._lock(table):
            path.unlink(missing_ok=True)

    def reset_alerts_if_empty(self):
        """
        clear eviction and age latches once nothing remains to drain
        :param self: this
        """
        if self._has_pending():
            return
        self._evict_alerted = False
        self._age_alerted = False

    def _has_pending(self) -> bool:
        """
        whether any segment or draining file remains
        :param self: this
        :return: True when the spool still holds rows
        """
        for table in self.tables():
            directory = self._folder / table
            if self.segments(table) or list(directory.glob("*.jsonl.draining")) or (directory / _WINDOW_NAME).is_file():
                return True
        return False

    @staticmethod
    def _read_window(path: Path) -> tuple[datetime | None, str | None]:
        """
        read replay-window metadata while the caller holds the table lock
        :param path: metadata path
        :return: read_time and repository path
        """
        if not path.is_file():
            return None, None
        body = json.loads(path.read_text(encoding="utf-8"))
        return datetime.fromisoformat(body["read_time"]), body.get("repository")

    def _segment_name(self) -> str:
        """
        active hourly segment name in UTC
        :param self: this
        :return: the file name
        """
        return datetime.now(timezone.utc).strftime("%Y%m%dT%H") + ".jsonl"

    def _lock(self, table: str) -> threading.Lock:
        """
        per-table lock shared by append and rename
        :param self: this
        :param table: the table directory name
        :return: the lock
        """
        with self._locks_guard:
            if table not in self._locks:
                self._locks[table] = threading.Lock()
            return self._locks[table]

    def _write_line(self, path: Path, line: str):
        """
        append one line and fsync it
        :param self: this
        :param path: the file
        :param line: the line
        """
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line if line.endswith("\n") else line + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    def _evict_until_fit(self, segment_name: str):
        """
        drop the oldest segment across tables until free space is above the floor
        :param self: this
        :param segment_name: the active segment name
        """
        while self._free_pct() < self._min_free_pct:
            victim = self._oldest_evictable(segment_name)
            if victim is None:
                self.logger.error("spool cannot free disk; no evictable segment")
                raise SpoolCapacityError(
                    f"cannot preserve {self._min_free_pct}% free space without deleting an active segment"
                )
            victim_table = victim.parent.name
            with self._lock(victim_table):
                if not victim.is_file() or not _SEGMENT_RE.match(victim.name):
                    continue
                rows = self._row_count(victim)
                victim.unlink()
            self.logger.error("evicted spool segment %s (%s rows)", victim, rows)
            if not self._evict_alerted:
                self._evict_alerted = True
                Emailer().send_alert(
                    "Spool eviction",
                    f"evicted spool segment {victim} ({rows} rows) to keep {self._min_free_pct}% free",
                )

    def _oldest_evictable(self, segment_name: str) -> Path | None:
        """
        oldest hourly segment that is not the active file and not draining
        :param self: this
        :param segment_name: the active segment name
        :return: the victim path
        """
        candidates = []
        for name in self.tables():
            for path in self.segments(name):
                if path.name == segment_name:
                    continue
                candidates.append(path)
        if not candidates:
            return None
        candidates.sort(key=lambda path: path.name)
        return candidates[0]

    def _warn_if_old(self):
        """
        one age warning per outage when the oldest segment passes the target
        :param self: this
        """
        if self._age_alerted:
            return
        oldest = self._oldest_segment()
        if oldest is None:
            return
        started = datetime.strptime(oldest.name[:11], "%Y%m%dT%H").replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - started <= timedelta(hours=self._warn_age_hours):
            return
        self._age_alerted = True
        Emailer().send_alert(
            "Spool age",
            f"oldest spool segment {oldest.name} is older than {self._warn_age_hours} hours",
        )

    def _oldest_segment(self) -> Path | None:
        """
        oldest hourly segment across tables
        :param self: this
        :return: the path
        """
        found = []
        for table in self.tables():
            found.extend(self.segments(table))
        if not found:
            return None
        found.sort(key=lambda path: path.name)
        return found[0]

    def _free_pct(self) -> float:
        """
        percent of the spool filesystem that is free
        :param self: this
        :return: free space percent
        """
        self._folder.mkdir(parents=True, exist_ok=True)
        usage = shutil.disk_usage(self._folder)
        if usage.total == 0:
            return 100.0
        return 100.0 * usage.free / usage.total

    @staticmethod
    def _row_count(path: Path) -> int:
        """
        count non-empty lines
        :param path: the segment
        :return: the row count
        """
        with path.open(encoding="utf-8") as handle:
            return sum(1 for line in handle if line.strip())
