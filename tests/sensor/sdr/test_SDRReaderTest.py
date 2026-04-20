import time
import unittest

import pytest

from sensor.sdr.SDRReader import SDRReader


@pytest.mark.integration
class SDRReaderTest(unittest.TestCase):
    def test(self):
        bs: SDRReader = SDRReader()
        bs.read()

        time.sleep(5)
        
        self.assertTrue(len(bs.reads) > 0)

        for d in bs.reads:
            self.assertIsNotNone(d.raw)
            self.assertIsNotNone(d.config)
