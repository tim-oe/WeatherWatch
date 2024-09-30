#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
#
"""
"""

# https://stackoverflow.com/questions/44834/can-someone-explain-all-in-python
__all__ = ["SDRReader"]

import datetime
import json
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
from queue import Empty, Queue
from subprocess import PIPE, STDOUT, Popen
from typing import List

from python_event_bus import EventBus

from conf.AppConfig import AppConfig
from conf.SensorConfig import SensorConfig
from sensor.sdr.BaseData import BaseData
from sensor.sdr.IndoorData import IndoorData
from sensor.sdr.OutdoorData import OutdoorData

__all__ = ["SDRReader"]


class SensorEvent(object):
    """
    class to allow for async event
    """

    def __init__(self, data: BaseData):
        """
        ctor
        :param self: this
        """
        self._data = data

    def fire(self):
        try:
            eventName = self._data.__class__.__name__
            logging.debug("fire " + eventName)
            EventBus.call(eventName, self._data)
        except Exception as e:
            logging.error("event processing error " + str(e))


class SDRReader(object):
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
    CMD_BASE = ["/usr/local/bin/rtl_433", "-q", "-M", "level", "-F", "json"]

    # override for singleton
    # https://www.geeksforgeeks.org/singleton-pattern-in-python-a-complete-guide/
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(SDRReader, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._appConfig: AppConfig = AppConfig()

        self._timeout = int(self._appConfig.conf[AppConfig.SDR_KEY][AppConfig.READER_KEY]["timeout"])

        # sensor read pool predefined thread
        self._readPool = ThreadPoolExecutor(max_workers=1)

        self._sensors: dict = {}
        self._cmd = SDRReader.CMD_BASE.copy()
        for s in self._appConfig.sensors:
            self._cmd.append(SDRReader.DEVICE_FLAG)
            self._cmd.append(str(s.device))
            self._sensors[s.key] = s

        # sensor data thread to fire event async
        self._dataPool = ThreadPoolExecutor(max_workers=len(self._sensors))

        self._reads = []

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
            for line in iter(out.readline, b""):
                try:
                    json.loads(line)
                    queue.put(line)
                except ValueError:
                    logging.debug(line.decode())
                    pass
        except Exception as e:
            logging.error("line processing error " + str(e))
            pass
        finally:
            logging.debug("line processing complete")
            out.close()

    def processRecord(self, line, sensors: dict, reads: List[BaseData]):
        """
        process sensor data
        """
        logging.debug("sensor json: " + line)
        j = json.loads(line)

        key = BaseData.key(j)

        if key in sensors:
            sensor: SensorConfig = sensors[key]
            r: BaseData = None
            match sensor.dataClass:
                case IndoorData.__name__:
                    r = json.loads(line, object_hook=IndoorData.jsonDecoder)
                case OutdoorData.__name__:
                    r = json.loads(line, object_hook=OutdoorData.jsonDecoder)
                case _:
                    logging.error("unkown impl for sensor: " + sensor)

            if r is not None:
                r.raw = json.loads(line)
                r.config = sensor
                reads.append(r)
                se: SensorEvent = SensorEvent(r)
                self._dataPool.submit(se.fire)

            del sensors[key]
        else:
            logging.debug("skipping: " + line)

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
        logging.debug("starting cmd: " + str(self._cmd))

        sensors = self._sensors.copy()
        self._reads = []
        reads = []

        p = Popen(
            self._cmd,
            stdout=PIPE,
            stderr=STDOUT,
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
                    pass  # time.sleep(1)
                else:  # got line
                    self.processRecord(data.decode(), sensors, reads)

                sys.stdout.flush()
                duration = self.duration(start)
                logging.debug("duration: " + str(duration) + " reads " + str(len(reads)))
            self._reads = reads
        except Exception as e:
            logging.error("sensor read failed " + str(e))
        finally:
            logging.info("stopping reader " + str(duration) + " sec, reads " + str(len(reads)))
            p.kill()

        for k, v in sensors.items():
            logging.error("no data for " + k + " =" + str(v))
