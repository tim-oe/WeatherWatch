import logging
import sys
from subprocess import Popen, TimeoutExpired

from py_singleton import singleton

__all__ = ["TimelapseSvc"]


@singleton
class TimelapseSvc:
    """
    currently encountering resource leak
    memory is not always freeing after video creation
    trying subprocess as restarting svc clears mem
    """

    ON_POSIX = "posix" in sys.builtin_module_names

    CMD = [sys.executable, "weatherwatch/timelapse.py"]

    def process(self):
        logging.info("starting timelapse subprocess")

        p: Popen = Popen(
            TimelapseSvc.CMD,
            close_fds=TimelapseSvc.ON_POSIX,
        )

        try:
            p.wait(timeout=60 * 15)
            logging.info("timelapse subprocess complete %s", p.returncode)
        except TimeoutExpired:
            logging.exception("processe timed out")
            p.kill()
