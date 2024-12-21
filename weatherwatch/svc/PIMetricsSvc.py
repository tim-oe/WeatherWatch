from concurrent import futures
from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor
from datetime import datetime

import psutil
import uptime
from entity.PIMetrics import PIMetrics
from py_singleton import singleton
from repository.PIMetricsRepository import PIMetricsRepository
from util.Logger import logger

__all__ = ["PIMetricsSvc"]


@logger
@singleton
class PIMetricsSvc:
    """
    Pi metric data service
    """

    def __init__(self):
        """
        ctor
        :param self: this
        """

        # sensor read pool predefined thread
        self._read_pool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=3)

        self._pi_metrics_repo: PIMetricsRepository = PIMetricsRepository()

    def get_memory(self, data: PIMetrics):
        """
        get memory
        :param self: this
        :param data: metrics data
        """
        mem = psutil.virtual_memory()
        data.mem_available = mem.available
        data.mem_used = mem.used
        data.mem_percent = mem.percent

    def get_disk(self, data: PIMetrics):
        """
        get disk
        :param self: this
        :param data: metrics data
        """
        disk = psutil.disk_usage("/")
        data.disk_available = disk.free
        data.disk_used = disk.used
        data.disk_percent = disk.percent

    def get_temp(self, data: PIMetrics):
        """
        get temp
        :param self: this
        :param data: metrics data
        """
        cpu = psutil.sensors_temperatures()
        data.cpu_temp_c = cpu["cpu_thermal"][0].current

    def get_metrics(self) -> PIMetrics:
        """
        get system metrics
        :param self: this
        """
        data: PIMetrics = PIMetrics()

        self.get_memory(data)
        self.get_disk(data)
        self.get_temp(data)

        return data

    def get_uptime(self) -> str:
        """
        Gets the system uptime and returns it in days, hours, minutes, and seconds.
        :param self: this
        """
        uptime_seconds = uptime.uptime()

        uptime_string = str(datetime.timedelta(seconds=uptime_seconds))
        self.logger.debug("uptime %s", uptime_string)

        return uptime_string

    def process(self):
        """
        service entry point
        :param self: this
        """
        data: PIMetrics = PIMetrics()

        fs: futures = []

        fs.append(self._read_pool.submit(self.get_memory, data))
        fs.append(self._read_pool.submit(self.get_disk, data))
        fs.append(self._read_pool.submit(self.get_temp, data))

        futures.wait(fs, timeout=None, return_when=ALL_COMPLETED)

        self.logger.debug("pi metrics %s", data)

        data.read_time = datetime.now()

        self._pi_metrics_repo.insert(data)
