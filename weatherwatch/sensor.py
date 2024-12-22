#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
application entry point
"""

import time

from svc.SchedulerSvc import SchedulerSvc

# actual start point
if __name__ == "__main__":

    ss: SchedulerSvc = SchedulerSvc()

    ss.start()

    while True:
        time.sleep(5)
