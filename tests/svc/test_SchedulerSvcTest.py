import unittest

from svc.SchedulerSvc import SchedulerSvc


class ScheduleSvcTest(unittest.TestCase):
    def test(self):
        svc: SchedulerSvc = SchedulerSvc()
        print(svc)
        svc.start()
        svc.pause()
