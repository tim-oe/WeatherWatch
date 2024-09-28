#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
#
"""
application entry point
https://pagure.io/python-daemon/
https://github.com/prehensilecode/python-daemon-example/blob/master/eg_daemon.py
"""

import argparse
import time

import daemon
from daemon import pidfile

from svc.SchedulerSvc import SchedulerSvc


def app_run():
    """
    application entry point
    """

    ss: SchedulerSvc = SchedulerSvc()

    ss.start()
    while True:
        time.sleep(5)


def start_daemon(pidf):
    """
    daemon initialization function
    """

    with daemon.DaemonContext(
        pidfile=pidfile.TimeoutPIDLockFile(pidf),
    ) as context:  # noqa
        app_run()


# actual start point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Example daemon in Python")
    parser.add_argument("-p", "--pid-file", default="/var/run/ww_daemon.pid")

    args = parser.parse_args()

    start_daemon(pidf=args.pid_file)
