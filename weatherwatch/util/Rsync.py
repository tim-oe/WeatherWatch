import sys
from datetime import datetime, timedelta
from pathlib import Path
from subprocess import Popen, TimeoutExpired

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

    def archive(self, src: str, dest: str):
        """
        archive data
        :param self: this
        :param src: the source folder
        :param dest: the destination folder
        """
        self.logger.info(f"starting rsync {src} -> {dest}")

        cmd = Rsync.BASE_CMD.copy()
        cmd.append(src)
        cmd.append(dest)

        with Popen(
            cmd,
            # stdout=PIPE,
            # stderr=PIPE,
            # text=True,
            close_fds=Rsync.ON_POSIX,
        ) as p:

            try:
                p.wait(timeout=60 * 5)
                self.logger.info("rsync subprocess complete %s", p.returncode)
                # for line in p.stdout:
                #     self.logger.debug(line.strip())

                # for line in p.stderr:
                #     self.logger.error(line.strip())
            except TimeoutExpired:
                self.logger.exception("rsync timed out")
                p.kill()

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
