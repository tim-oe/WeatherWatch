import sys
from datetime import datetime, timedelta
from pathlib import Path
from subprocess import PIPE, Popen, TimeoutExpired

from util.Logger import logger

__all__ = ["Rsync"]


@logger
class Rsync:
    """
    simple wrapper around rsync, assumes on path
    would be nice pure python, but this is only supported on a PI
    """

    ON_POSIX = "posix" in sys.builtin_module_names

    BASE_CMD = ["rsync", "-a", "--no-perms", "--no-owner", "--no-group"]

    ARCHIVE_TIMEOUT = 60 * 5

    def archive(self, src: str, dest: str) -> bool:
        """
        archive data
        :param self: this
        :param src: the source folder
        :param dest: the destination folder
        :return: True when rsync exits 0
        """
        self.logger.info("starting rsync %s -> %s", src, dest)

        cmd = list(self.BASE_CMD)
        cmd.append(src)
        cmd.append(dest)

        with Popen(
            cmd,
            stderr=PIPE,
            text=True,
            close_fds=Rsync.ON_POSIX,
        ) as process:
            try:
                _, err = process.communicate(timeout=self.ARCHIVE_TIMEOUT)
            except TimeoutExpired:
                self.logger.error("rsync timed out")
                process.kill()
                process.wait()
                return False

            if process.returncode != 0:
                self.logger.error("rsync failed %s: %s", process.returncode, (err or "").strip())
                return False

            self.logger.info("rsync subprocess complete %s", process.returncode)
            return True

    def purge(self, src: str, days_ago: int):
        """
        purge data older than a given days from current date
        :param self: this
        :param src: the source folder
        :param days_ago: the days to purge data
        """
        cutoff_date = datetime.now() - timedelta(days=days_ago)
        src_dir: Path = Path(src)

        for file in src_dir.iterdir():
            if file.is_file():
                file_stat = file.stat()
                modification_time = datetime.fromtimestamp(file_stat.st_mtime)

                if modification_time < cutoff_date:
                    file.unlink()
