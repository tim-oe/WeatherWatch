import unittest

from svc.TimelapseSvc import TimelapseSvc


class TimelapseSvcTest(unittest.TestCase):
    def test(self):
        svc: TimelapseSvc = TimelapseSvc()
        
        svc.process()
        # TODO verify?