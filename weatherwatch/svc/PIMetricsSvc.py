import datetime
import logging
from concurrent import futures
from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor

import psutil
from entity.PIMetrics import PIMetrics
from py_singleton import singleton
from repository.PIMetricsRepository import PIMetricsRepository

__all__ = ["PIMetricsSvc"]

"""
Pi metric data service
"""


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

    def process(self):
        data: PIMetrics = PIMetrics()

        fs: futures = []

        fs.append(self._readPool.submit(self.getMem, data))
        fs.append(self._readPool.submit(self.getDisk, data))
        fs.append(self._readPool.submit(self.getTemp, data))

        futures.wait(fs, timeout=None, return_when=ALL_COMPLETED)

        logging.debug("pi metrics %s", data)

        data.read_time = datetime.datetime.now()

        self._piMetricsRepo.insert(data)
