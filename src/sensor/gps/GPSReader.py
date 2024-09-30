#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
#
"""
"""

# https://stackoverflow.com/questions/44834/can-someone-explain-all-in-python
__all__ = ["GPSReader"]

import json
import logging
import sys
import time
from queue import Empty, Queue
from subprocess import PIPE, STDOUT, Popen
from threading import Thread

from conf.AppConfig import AppConfig
from util.Singleton import Singleton

__all__ = ["GPSReader"]


# TODO test...


class GPSReader(Singleton):
    """
    gps reader for lon lat alt
    """

    ON_POSIX = "posix" in sys.builtin_module_names

    # https://manpages.ubuntu.com/manpages/trusty/man1/gpspipe.1.html
    CMD = ["gpspipe", "-w", "-n", "5", "|", "grep", "-m", "1", '\'{"class":"TPV".*}\'']

    def __init__(self):
        """
        ctor
        :param self: this
        """
        if self._initialized:
            return
        self._initialized = True

        self._appConfig: AppConfig = AppConfig()
        self._record = None

    @property
    def record(self):
        """
        record string property getter
        :param self: this
        :return: the record
        """
        return self._record

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

    def processRecord(self, line):
        """
        process sensor data
        """
        logging.debug("sensor json: " + line)
        self._record = json.loads(line)

    def read(self):
        """
        read sensor data
        this will block until all sensors are read or until timeout
        """
        logging.info("starting cmd: " + str(GPSReader.CMD))

        self.p = Popen(GPSReader.CMD, stdout=PIPE, stderr=STDOUT, close_fds=GPSReader.ON_POSIX)

        self.q = Queue()

        self.t = Thread(target=self.pushRecord, args=(self.p.stdout, self.q))

        self.t.daemon = True  # thread dies with the program
        self.t.start()

        self._record = None

        try:
            while self._record is None:
                try:
                    data = self.q.get(timeout=4)
                except Empty:
                    time.sleep(1)
                else:  # got line
                    self.processRecord(data.decode())

                sys.stdout.flush()
        except Exception as e:
            logging.error("sensor read failed " + str(e))
            raise Exception("sensor read failed ") from e
        finally:
            self.p.kill()
