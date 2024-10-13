#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
#
"""
application entry point
"""

import logging
import time

from picamera2 import Picamera2
from svc.SchedulerSvc import SchedulerSvc

# actual start point
if __name__ == "__main__":

    # https://forums.raspberrypi.com/viewtopic.php?t=364677
    Picamera2.set_logging(level=logging.WARN, output=None)

    ss: SchedulerSvc = SchedulerSvc()

    ss.start()

    while True:
        time.sleep(5)
