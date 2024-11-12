import unittest

from svc.PIMetricsSvc import PIMetricsSvc


class ScheduleSvcTest(unittest.TestCase):
    def test(self):
        svc: PIMetricsSvc = PIMetricsSvc()
        svc.process()
