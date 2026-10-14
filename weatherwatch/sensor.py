#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
application entry point
"""

import time

from sensor.sdr.SDRReader import SDRReader
from svc.SchedulerSvc import SchedulerSvc

# actual start point
if __name__ == "__main__":

    # startup diagnostic: detect the SDR usb dongle before scheduling reads
    SDRReader()

    ss: SchedulerSvc = SchedulerSvc()

    ss.start()

    while True:
        time.sleep(5)
