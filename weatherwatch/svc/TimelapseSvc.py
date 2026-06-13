import sys
import time
from subprocess import Popen, TimeoutExpired

from py_singleton import singleton
from util.Converter import Converter
from util.Logger import logger

__all__ = ["TimelapseSvc"]


@logger
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
        """
        service entry point
        :param self: this
        """
        start_monotonic = time.monotonic()

        with Popen(
            TimelapseSvc.CMD,
            # stdout=PIPE,
            # stderr=PIPE,
            # text=True,
            close_fds=TimelapseSvc.ON_POSIX,
        ) as p:

            try:
                p.wait(timeout=60 * 15)
                self.logger.info("timelapse subprocess complete %s", p.returncode)
                # for line in p.stdout:
                #     self.logger.debug(line.strip())

                # for line in p.stderr:
                #     self.logger.error(line.strip())
            except TimeoutExpired:
                self.logger.exception("process timed out")
                p.kill()

        self.logger.info("timelapse processing complete  duration %s", Converter.duration_seconds(start_monotonic))
