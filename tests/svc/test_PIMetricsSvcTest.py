import unittest

from src.svc.PIMetricsSvc import PIMetricsSvc


class ScheduleSvcTest(unittest.TestCase):
    def test(self):
        svc: PIMetricsSvc = PIMetricsSvc()
        svc.process()
