#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
#
"""
"""

import datetime
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from queue import Empty, Queue
from subprocess import PIPE, Popen
from typing import List

from conf.AppConfig import AppConfig
from conf.SensorConfig import SensorConfig
from entity.SDRMetricts import SDRMetrics
from py_singleton import singleton
from python_event_bus import EventBus
from repository.SDRMetricsRepository import SDRMetricsRepository
from sensor.sdr.BaseData import BaseData
from sensor.sdr.IndoorData import IndoorData
from sensor.sdr.OutdoorData import OutdoorData
from util.Logger import logger

__all__ = ["SDRReader"]


@logger
class SensorEvent:
    """
    class to allow for async event
    """

    def __init__(self, evt: str, data: BaseData):
        """
        ctor
        :param self: this
        """
        self._data = data
        self._evt = evt

    def fire(self):
        self.logger.debug("fire %s", self._evt)

        try:
            EventBus.call(self._evt, self._data)
        except Exception:
            self.logger.exception("event processing error %s data\n%s", self._evt, self._data)


@logger
@singleton
class SDRReader:
    """
    RTL-SDR sensor reader
    lib: https://github.com/merbanan/rtl_433
    dev receiver: https://www.nooelec.com/store/sdr/sdr-receivers/nesdr-smart-sdr.html?srsltid=AfmBOoqsEaIcHnJ1mghLBbE5q-Gf0NjyJYp46zaCQwDXRngPQauzruzT
    nano receiver: https://www.nooelec.com/store/nesdr-nano-three.html?srsltid=AfmBOoqo75MWaw153HkAv74eAI2DQ20mXLbyGMAAxUaYlXcehXMSOOzr
    indoor: /usr/local/bin/rtl_433 -M level -F json -R 20
    outdoor: /usr/local/bin/rtl_433 -M level -F json -R 153
    """  # noqa

    ON_POSIX = "posix" in sys.builtin_module_names
    DEVICE_FLAG = "-R"
    CMD_BASE = ["/usr/local/bin/rtl_433", "-q", "-M", "level", "-F", "log", "-F", "json"]

    def __init__(self):
        """
        ctor
        :param self: this
        """

        self._appConfig: AppConfig = AppConfig()

        self._timeout = self._appConfig.conf[AppConfig.SDR_KEY][AppConfig.READER_KEY]["timeout"]

        # sensor read pool predefined thread
        self._readPool = ThreadPoolExecutor(max_workers=1)

        self._sensors: dict = {}
        self._cmd = SDRReader.CMD_BASE.copy()
        for s in self._appConfig.sensors:
            self._cmd.append(SDRReader.DEVICE_FLAG)
            self._cmd.append(str(s.device))
            self._sensors[s.key] = s

        self.logger.info(str(self._sensors))

        # sensor data thread to fire event async
        self._dataPool = ThreadPoolExecutor(max_workers=len(self._sensors))

        self._reads = []

        self._sdrMetricsRepo = SDRMetricsRepository()

    # override
    def __del__(self):
        self._readPool.shutdown()
        self._dataPool.shutdown()

    @property
    def reads(self) -> List[BaseData]:
        """
        reads string property getter
        :param self: this
        :return: the reads
        """
        return self._reads

    def pushRecord(self, out, queue):
        """
        push sensor data (will be json) to queue
        :param src: the source name (not used)
        :param out: the output buffer to read data from
        :param queue: the queue to push data to
        """
        try:
            for line in out:
                try:
                    json.loads(line)
                    queue.put(line.strip())
                except ValueError:
                    self.logger.debug(line)
                    pass
        except Exception:
            self.logger.exception("line processing error")
            pass
        finally:
            out.close()

    def processRecord(self, line: str, sensors: dict, reads: List[BaseData], processed: List[str]):
        """
        process sensor data
        """
        self.logger.debug("sensor json: %s", line)
        j = json.loads(line)

        key = BaseData.key(j)

        if key in sensors:
            sensor: SensorConfig = sensors[key]
            r: BaseData = None
            evt = None
            match sensor.data_class:
                case IndoorData.__name__:
                    r = json.loads(line, object_hook=IndoorData.jsonDecoder)
                    evt = IndoorData.__name__
                case OutdoorData.__name__:
                    r = json.loads(line, object_hook=OutdoorData.jsonDecoder)
                    evt = OutdoorData.__name__
                case _:
                    self.logger.error("unkown impl for sensor: %s", sensor)

            if r is not None:
                r.raw = json.loads(line)
                r.config = sensor
                reads.append(r)
                # EventBus.call(evt, r)
                se: SensorEvent = SensorEvent(evt, r)
                self._dataPool.submit(se.fire)

            del sensors[key]
            processed.append(key)
        else:
            if key not in processed:
                self.logger.warning("skipping: %s\n%s", key, line)

    def duration(self, start: datetime) -> int:
        """
        calculate the execution duration from start to now
        """
        current = datetime.datetime.now()
        return int((current - start).total_seconds())

    def read(self):
        """
        read sensor data
        this will block until all sensors are read or until timeout
        """
        self.logger.debug("starting cmd: %s", self._cmd)

        sensors = self._sensors.copy()
        processed = []
        self._reads = []
        reads = []

        p = Popen(
            self._cmd,
            stdout=PIPE,
            stderr=PIPE,
            text=True,
            close_fds=SDRReader.ON_POSIX,
        )

        q = Queue()

        # read sdr output
        self._readPool.submit(self.pushRecord, p.stdout, q)

        start = datetime.datetime.now()
        duration = 0
        try:
            while len(reads) < len(self._sensors) and duration < self._timeout:
                try:
                    data = q.get(timeout=10)
                except Empty:
                    pass
                else:  # got line
                    self.processRecord(data, sensors, reads, processed)

                sys.stdout.flush()
                duration = self.duration(start)

                self.logger.debug("duration: %s reads %s", duration, len(reads))
            self._reads = reads
            self.logMetrics(start, datetime.datetime.now(), duration, len(reads))
        except Exception:
            self.logger.exception("sensor read failed")
        finally:
            self.logger.info("stopping reader %s sec, reads %s", duration, len(reads))
            p.kill()

        for k, v in sensors.items():
            self.logger.error("no data for %s=\n%s", k, v)

    def logMetrics(self, startTime: datetime, endTime: datetime, duration: int, sensorCnt: int):
        try:
            m: SDRMetrics = SDRMetrics()
            m.start_time = startTime
            m.end_time = endTime
            m.duration_sec = duration
            m.sensor_cnt = sensorCnt

            self._sdrMetricsRepo.insert(m)
        except Exception:
            self.logger.exception("sensor read failed")
