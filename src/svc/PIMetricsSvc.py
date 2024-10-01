from concurrent import futures
from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor
import datetime
import logging
import subprocess
from py_singleton import singleton

from entity.PiMetrics import PIMetrics
from repository.PIMetricsRepository import PIMetricsRepository

__all__ = ["PiMetricsSvc"]

@singleton
class PIMetricsSvc(object):
    MEM_CMD = ['bash','-c','free -gh --si | egrep -o Mem:.* | sed -E "s/\Mem:\s+([0-9\.]+[GMK]?)\s+([0-9\.]+[GMK]?)\s+([0-9\.]+[GMK]?)\s+([0-9\.]+[GMK]?)\s+([0-9\.]+[GMK]?)\s+([0-9\.]+[GMK]?)/total: \\1 used: \\2 free: \\3/"']
    DISK_CMD = ['bash','-c','df -h / | egrep -o /dev/.* | sed -E "s/\/dev\/[^\s]+\s+([0-9]+[GM]?)\s+([0-9\.]+[GM]?)\s+([0-9\.]+[GM]?).*/used: \\1 avaiable: \\2 free: \\3%/"']
    TEMP_CMD = ['bash','-c','vcgencmd measure_temp | egrep -o "[0-9]*\.[0-9]*.{2}"']

    def __init__(self):
        """
        ctor
        :param self: this
        """

        # sensor read pool predefined thread
        self._readPool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=3)

        self._piMetricsRepo: PIMetricsRepository = PIMetricsRepository()

    def getMem(self, data: PIMetrics):
        result = subprocess.run(PIMetricsSvc.MEM_CMD, capture_output=True, text=True, encoding="utf-8")
        data.mem_info = result.stdout.strip() 

    def getDisk(self, data: PIMetrics):
        result = subprocess.run(PIMetricsSvc.DISK_CMD, capture_output=True, text=True, encoding="utf-8")
        data.disk_info = result.stdout.strip() 

    def getTemp(self, data: PIMetrics):
        result = subprocess.run(PIMetricsSvc.TEMP_CMD, capture_output=True, text=True, encoding="utf-8")
        data.cpu_temp = result.stdout.strip()

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