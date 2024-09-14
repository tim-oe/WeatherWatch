#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
#
"""
"""

# https://stackoverflow.com/questions/44834/can-someone-explain-all-in-python
__all__ = ["SensorReader"]

from sensor.sdr.IndoorData import IndoorData
from sensor.sdr.OutdoorData import OutdoorData

from subprocess import PIPE, Popen, STDOUT
from threading  import Thread
from queue import Queue, Empty
import time
import sys
import json
import logging

class SensorReader(object):
    """
    base RTL-SDR sensor reader
    lib: https://github.com/merbanan/rtl_433
    reciever: https://www.nooelec.com/store/sdr/sdr-receivers/nesdr-smart-sdr.html?srsltid=AfmBOoqsEaIcHnJ1mghLBbE5q-Gf0NjyJYp46zaCQwDXRngPQauzruzT
    """
    ON_POSIX = 'posix' in sys.builtin_module_names
    CMD = ['/usr/local/bin/rtl_433', '-q', '-M', 'level', '-F', 'json', '-R', '20']
    #CMD = ['/usr/local/bin/rtl_433', '-q', '-M', 'level', '-F', 'json', '-R', '153']

    def __init__(self):
        """
        ctor
        :param self: this
        """

    def pushRecord(self, out, queue):
        """
        push sensor data (will be json) to queue
        :param src: the source name (not used)
        :param out: the output buffer to read data from
        :param queue: the queue to push data to
        """
        try:
            for line in iter(out.readline, b''):
                try:                   
                    json.loads(line) 
                    # TODO () -> k,v pair?
                    queue.put(line)
                except ValueError as e:
                    logging.info(line)
                    pass 
            out.close()
        except:
            pass 

    def read(self):
        """
        read sensor data
        """        
        logging.debug('starting cmd: ' + str(SensorReader.CMD))

        self.p = Popen( SensorReader.CMD, 
                       stdout=PIPE, 
                       stderr=STDOUT, 
                       bufsize=1, 
                       close_fds=SensorReader.ON_POSIX)
        self.q = Queue()

        self.t = Thread(target=self.pushRecord, 
                        args=(self.p.stdout, 
                        self.q))

        self.t.daemon = True # thread dies with the program
        self.t.start()

        while True:
            try:
                data = self.q.get(timeout = 5)
            except Empty:
                time.sleep(5)
            else: # got line
                logging.debug('sensor json: ' + data.decode())
                record: IndoorData = json.loads(data, object_hook = IndoorData.jsonDecoder)
                #record: OutdoorData = json.loads(data, object_hook = OutdoorData.jsonDecoder)
                logging.debug('sensor instance: ' + str(record))

            sys.stdout.flush()