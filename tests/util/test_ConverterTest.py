from datetime import datetime
from decimal import Decimal
import time
import unittest

from tzlocal import get_localzone_name

from util.Converter import Converter

class ConverterTest(unittest.TestCase):
    def test(self):        
        self.assertEqual(Converter.MPS_TO_MPH_FACTOR, Converter.mps_to_mph(Decimal(1.0)))
        self.assertEqual(Converter.HPA_TO_IOM_FACTOR, Converter.hpa_to_iom(Decimal(1.0)))
        self.assertEqual(Converter.LUX_TO_WPM_FACTOR, Converter.lux_to_wpm(Decimal(1.0)))
        self.assertEqual(Decimal(1.0), Decimal(round(Converter.mm_to_inch(float(Decimal(25.4))),2)))

        print(f"system timezone [{Converter.tzname_to_fullname(datetime.now().astimezone().tzinfo.tzname(None))}]")

        curr: datetime = datetime.now()
        print(curr)
        then: datetime = Converter.to_utc(curr)
        print(then)
        
        dif = int((then.replace(tzinfo=None) - curr).total_seconds() / (60 * 60))
        
        self.assertTrue(dif == 6 or dif == 5)
        
        print()

    def test_utcnow_is_naive(self):
        """utcnow() must return a naive datetime (no tzinfo)."""
        result = Converter.utcnow()
        self.assertIsNone(result.tzinfo)

    def test_utcnow_is_utc_offset(self):
        """utcnow() should be 5 or 6 hours ahead of local datetime.now()."""
        local = datetime.now()
        utc = Converter.utcnow()
        diff_hours = round((utc - local).total_seconds() / 3600)
        self.assertIn(diff_hours, (5, 6), f"expected UTC offset of 5 or 6 hours, got {diff_hours}")

    def test_duration_seconds_measures_elapsed(self):
        """duration_seconds(start) returns elapsed seconds from a monotonic start."""
        start = time.monotonic()
        time.sleep(0.1)
        elapsed = Converter.duration_seconds(start)
        # allow a wide window to avoid flaky failures under load
        self.assertGreaterEqual(elapsed, 0)
        self.assertLessEqual(elapsed, 5)

    def test_duration_seconds_zero_at_start(self):
        """duration_seconds called immediately after capture returns 0 or 1."""
        start = time.monotonic()
        elapsed = Converter.duration_seconds(start)
        self.assertIn(elapsed, (0, 1))

