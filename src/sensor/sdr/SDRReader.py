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
import time
from queue import Empty, Queue
from subprocess import PIPE, STDOUT, Popen
from threading import Thread
from typing import List

from sensor.sdr.BaseData import BaseData
from sensor.sdr.IndoorData import IndoorData
from sensor.sdr.OutdoorData import OutdoorData
from src.conf.AppConfig import AppConfig
from src.conf.SensorConfig import SensorConfig

__all__ = ["SDRReader"]


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
    CMD = ["/usr/local/bin/rtl_433", "-q", "-M", "level", "-F", "json"]

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

        self._sensors: dict = {}
        for s in self._appConfig.sensors:
            SDRReader.CMD.append(SDRReader.DEVICE_FLAG)
            SDRReader.CMD.append(str(s.device))
            self._sensors[s.key] = s

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
                    # TODO () -> k,v pair?
                    queue.put(line)
                except ValueError:
                    logging.info(line.decode())
                    pass
            out.close()
        except Exception:
            pass

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

            del sensors[key]
        else:
            logging.debug("skipping: " + line)

    def duration(self, start: datetime) -> int:
        """
        read sensor data
        """
        current = datetime.datetime.now()
        return int((current - start).total_seconds())

    def read(self):
        """
        read sensor data
        this will block until all sensors are read or until timeout
        """
        logging.info("starting cmd: " + str(SDRReader.CMD))

        sensors = self._sensors.copy()
        self._reads = []
        reads = []

        self.p = Popen(
            SDRReader.CMD,
            stdout=PIPE,
            stderr=STDOUT,
            close_fds=SDRReader.ON_POSIX,
        )

        self.q = Queue()

        self.t = Thread(target=self.pushRecord, args=(self.p.stdout, self.q))

        self.t.daemon = True  # thread dies with the program
        self.t.start()

        start = datetime.datetime.now()
        duration = 0
        try:
            while len(reads) < len(self._sensors) and duration < self._timeout:
                try:
                    data = self.q.get(timeout=4)
                except Empty:
                    time.sleep(1)
                else:  # got line
                    self.processRecord(data.decode(), sensors, reads)

                sys.stdout.flush()
                duration = self.duration(start)
                logging.debug("duration: " + str(duration) + " reads " + str(len(reads)))
            self._reads = reads
        except Exception as e:
            logging.error("sensor read failed " + str(e))
            raise Exception("sensor read failed ") from e
        finally:
            logging.info("stopping reader " + str(duration) + " reads " + str(len(reads)))
            self.p.kill()

        for k, v in sensors.items():
            logging.error("no data for " + k + " =" + str(v))
