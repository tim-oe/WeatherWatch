import unittest

from src.svc.SchedulerSvc import SchedulerSvc


class ScheduleSvcTest(unittest.TestCase):
    def test(self):
        svc: SchedulerSvc = SchedulerSvc()
        print(svc)