import unittest

from src.sensor.sdr.SDRReader import SDRReader

class SDRReaderTest(unittest.TestCase):
    def test(self):
        bs: SDRReader = SDRReader()

        bs.read()

        self.assertTrue(len(bs.reads) > 0)
