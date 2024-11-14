import datetime
from concurrent import futures
from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor

import psutil
import uptime
from entity.PIMetrics import PIMetrics
from py_singleton import singleton
from repository.PIMetricsRepository import PIMetricsRepository
from util.Logger import logger

__all__ = ["PIMetricsSvc"]

"""
Pi metric data service
"""


@logger
@singleton
class PIMetricsSvc:

    def __init__(self):
        """
        ctor
        :param self: this
        """

        # sensor read pool predefined thread
        self._readPool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=3)

        self._piMetricsRepo: PIMetricsRepository = PIMetricsRepository()

    def getMem(self, data: PIMetrics):
        mem = psutil.virtual_memory()
        data.mem_available = mem.available
        data.mem_used = mem.used
        data.mem_percent = mem.percent

    def getDisk(self, data: PIMetrics):
        disk = psutil.disk_usage("/")
        data.disk_available = disk.free
        data.disk_used = disk.used
        data.disk_percent = disk.percent

    def getTemp(self, data: PIMetrics):
        cpu = psutil.sensors_temperatures()
        data.cpu_temp_c = cpu["cpu_thermal"][0].current

    def getMetrics(self) -> PIMetrics:
        data: PIMetrics = PIMetrics()

        self.getMem(data)
        self.getDisk(data)
        self.getTemp(data)

        return data

    def getUptime(self) -> str:
        """
        Gets the system uptime and returns it in days, hours, minutes, and seconds.
        """
        uptime_seconds = uptime.uptime()

        uptime_string = str(datetime.timedelta(seconds=uptime_seconds))
        self.logger.debug("uptime %s", uptime_string)

        return uptime_string

    def process(self):
        data: PIMetrics = PIMetrics()

        fs: futures = []

        fs.append(self._readPool.submit(self.getMem, data))
        fs.append(self._readPool.submit(self.getDisk, data))
        fs.append(self._readPool.submit(self.getTemp, data))

        futures.wait(fs, timeout=None, return_when=ALL_COMPLETED)

        self.logger.debug("pi metrics %s", data)

        data.read_time = datetime.datetime.now()

        self._piMetricsRepo.insert(data)
