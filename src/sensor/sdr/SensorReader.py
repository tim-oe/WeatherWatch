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
from sensor.sdr.BaseData import BaseData

from src.conf.AppConfig import AppConfig
from src.conf.SensorConfig import SensorConfig

from subprocess import PIPE, Popen, STDOUT
from threading  import Thread
from queue import Queue, Empty
import datetime
import time
import sys
import json
import logging
from typing import List

class SensorReader(object):
    """
    base RTL-SDR sensor reader
    lib: https://github.com/merbanan/rtl_433
    reciever: https://www.nooelec.com/store/sdr/sdr-receivers/nesdr-smart-sdr.html?srsltid=AfmBOoqsEaIcHnJ1mghLBbE5q-Gf0NjyJYp46zaCQwDXRngPQauzruzT
    """
    ON_POSIX = 'posix' in sys.builtin_module_names
    DEVICE_FLAG = '-R'
    CMD = ['/usr/local/bin/rtl_433', '-q', '-M', 'level', '-F', 'json']
    
    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._appConfig: AppConfig = AppConfig()
        self._timeout = self._appConfig.conf[AppConfig.SDR_KEY][AppConfig.READER_KEY]['timeout']

        self._sensors: dict = {}
        for s in self._appConfig.sensors:
            SensorReader.CMD.append(SensorReader.DEVICE_FLAG)
            SensorReader.CMD.append(str(s.device))
            self._sensors[s.key] = s
        
        self._reads = []    

    @property
    def reads(self) -> List[BaseData]:
        """
        rain_mm string property getter
        :param self: this
        :return: the rain_mm
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
            for line in iter(out.readline, b''):
                try:                   
                    json.loads(line) 
                    # TODO () -> k,v pair?
                    queue.put(line)
                except ValueError as e:
                    logging.info(line.decode())
                    pass 
            out.close()
        except:
            pass 

    def processRecord(self, line, sensors: dict, reads: List[BaseData]):
        """
        process sensor data
        """        
        logging.debug('sensor json: ' + line)
        j = json.loads(line)
        
        key = BaseData.key(j)
        
        if key in sensors:
            sensor: SensorConfig = sensors[key]
            match sensor.dataClass:
                case IndoorData.__name__:
                    reads.append(json.loads(line, object_hook = IndoorData.jsonDecoder))
                case OutdoorData.__name__:
                    reads.append(json.loads(line, object_hook = OutdoorData.jsonDecoder))
                case _:
                    logging.error('unkown impl for sensor: ' + sensor)
            del sensors[key]
        else:    
            logging.debug('skipping: ' + line)

    def duration(self, start: datetime) -> int:
        """
        read sensor data
        """        
        current = datetime.datetime.now()
        return int((current-start).total_seconds())
                  
    def read(self):
        """
        read sensor data
        this will block until all sensors are read or until timeout
        """        
        logging.info('starting cmd: ' + str(SensorReader.CMD))

        sensors = self._sensors.copy()
        reads = []    

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

        start = datetime.datetime.now()
        duration = 0
        try:
            while len(reads) < len(self._sensors) and duration < self._timeout:
                try:
                    data = self.q.get(timeout = 4)
                except Empty:
                    time.sleep(1)
                else: # got line
                    self.processRecord(data.decode(), sensors, reads)

                sys.stdout.flush()
                duration = self.duration(start)
                logging.debug('duration: ' + str(duration) + ' reads ' + str(len(reads)))            
            self._reads = reads
        except Exception as e:
            logging.error('sensor read failed ' + str(e))            
            raise Exception('sensor read failed ') from e
        finally:        
            logging.info('stopping reader ' + str(duration) + ' reads ' + str(len(reads)))
            self.p.kill()

        for k, v in sensors.items():
            logging.error('no data for ' + k + ' =' + str(v))
            