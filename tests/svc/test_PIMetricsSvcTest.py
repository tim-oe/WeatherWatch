import unittest

from weatherwatch.svc.PIMetricsSvc import PIMetricsSvc


class ScheduleSvcTest(unittest.TestCase):
    def test(self):
        svc: PIMetricsSvc = PIMetricsSvc()
        svc.process()
