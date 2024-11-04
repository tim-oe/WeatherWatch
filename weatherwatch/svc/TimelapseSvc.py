import logging
import sys
from subprocess import Popen

from py_singleton import singleton

__all__ = ["TimelapseSvc"]


@singleton
class TimelapseSvc:
    ON_POSIX = "posix" in sys.builtin_module_names

    CMD = [sys.executable, "weatherwatch/timelapse.py"]

    def process(self):
        logging.info("starting timelapse subprocess")

        p = Popen(
            TimelapseSvc.CMD,
            close_fds=TimelapseSvc.ON_POSIX,
        )

        p.wait()
        logging.info("timelapse subprocess complete %s", p.returncode)
