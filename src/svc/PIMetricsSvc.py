import datetime
import logging
from concurrent import futures
from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor

import gpiozero
import psutil
from py_singleton import singleton

from repository.PIMetricsRepository import PIMetricsRepository
from src.entity.PIMetrics import PIMetrics

__all__ = ["PIMetricsSvc"]


@singleton
class PIMetricsSvc(object):

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
        cpu = gpiozero.CPUTemperature()
        data.cpu_temp_c = cpu.temperature

    def process(self):
        data: PIMetrics = PIMetrics()

        fs: futures = []

        fs.append(self._readPool.submit(self.getMem, data))
        fs.append(self._readPool.submit(self.getDisk, data))
        fs.append(self._readPool.submit(self.getTemp, data))

        futures.wait(fs, timeout=None, return_when=ALL_COMPLETED)

        logging.debug("pi metrics" + str(data))

        data.read_time = datetime.datetime.now()

        self._piMetricsRepo.insert(data)