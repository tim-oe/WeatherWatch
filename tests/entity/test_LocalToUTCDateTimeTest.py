import unittest
from datetime import date, datetime

import pytz

from entity.types import LocalToUTCDateTime

# America/Chicago offsets:
#   CDT (summer, UTC-5): 10:00 local -> 15:00 UTC
#   CST (winter, UTC-6): 10:00 local -> 16:00 UTC
CDT_LOCAL = datetime(2026, 7, 15, 10, 0, 0)
CDT_UTC = datetime(2026, 7, 15, 15, 0, 0)

CST_LOCAL = datetime(2026, 1, 15, 10, 0, 0)
CST_UTC = datetime(2026, 1, 15, 16, 0, 0)

# DST fall-back: 2026-11-01 01:30 is ambiguous (CDT or CST).
# is_dst=False -> picks CST (UTC-6) -> UTC 07:30
DST_FALLBACK_LOCAL = datetime(2026, 11, 1, 1, 30, 0)
DST_FALLBACK_UTC = datetime(2026, 11, 1, 7, 30, 0)


class LocalToUTCDateTimeTest(unittest.TestCase):
    """
    Unit tests for LocalToUTCDateTime TypeDecorator.
    Verifies that the persistence layer correctly translates between
    naive local (America/Chicago) datetimes and naive UTC datetimes
    without any UTC knowledge leaking into the application layer.
    """

    def setUp(self):
        self.typ = LocalToUTCDateTime()

    # ------------------------------------------------------------------
    # process_bind_param  (write path: local -> UTC)
    # ------------------------------------------------------------------

    def test_bind_cdt_converts_to_utc(self):
        result = self.typ.process_bind_param(CDT_LOCAL, None)
        self.assertEqual(CDT_UTC, result)

    def test_bind_cst_converts_to_utc(self):
        result = self.typ.process_bind_param(CST_LOCAL, None)
        self.assertEqual(CST_UTC, result)

    def test_bind_microseconds_preserved(self):
        local = datetime(2026, 7, 15, 10, 30, 45, 123456)
        result = self.typ.process_bind_param(local, None)
        self.assertEqual(datetime(2026, 7, 15, 15, 30, 45, 123456), result)

    def test_bind_result_is_naive(self):
        result = self.typ.process_bind_param(CDT_LOCAL, None)
        self.assertIsNone(result.tzinfo, "stored UTC value must be timezone-naive")

    def test_bind_none_returns_none(self):
        self.assertIsNone(self.typ.process_bind_param(None, None))

    def test_bind_dst_fallback_picks_cst(self):
        """Ambiguous fall-back hour: is_dst=False picks standard time (CST, UTC-6)."""
        result = self.typ.process_bind_param(DST_FALLBACK_LOCAL, None)
        self.assertEqual(DST_FALLBACK_UTC, result)

    # ------------------------------------------------------------------
    # process_result_value  (read path: UTC -> local)
    # ------------------------------------------------------------------

    def test_result_cdt_converts_to_local(self):
        result = self.typ.process_result_value(CDT_UTC, None)
        self.assertEqual(CDT_LOCAL, result)

    def test_result_cst_converts_to_local(self):
        result = self.typ.process_result_value(CST_UTC, None)
        self.assertEqual(CST_LOCAL, result)

    def test_result_microseconds_preserved(self):
        utc = datetime(2026, 7, 15, 15, 30, 45, 123456)
        result = self.typ.process_result_value(utc, None)
        self.assertEqual(datetime(2026, 7, 15, 10, 30, 45, 123456), result)

    def test_result_is_naive(self):
        result = self.typ.process_result_value(CDT_UTC, None)
        self.assertIsNone(result.tzinfo, "returned local datetime must be timezone-naive")

    def test_result_none_returns_none(self):
        self.assertIsNone(self.typ.process_result_value(None, None))

    # ------------------------------------------------------------------
    # Round-trip  (write then read must return the original local value)
    # ------------------------------------------------------------------

    def test_round_trip_cdt(self):
        utc = self.typ.process_bind_param(CDT_LOCAL, None)
        back = self.typ.process_result_value(utc, None)
        self.assertEqual(CDT_LOCAL, back)

    def test_round_trip_cst(self):
        utc = self.typ.process_bind_param(CST_LOCAL, None)
        back = self.typ.process_result_value(utc, None)
        self.assertEqual(CST_LOCAL, back)

    def test_round_trip_microseconds(self):
        local = datetime(2026, 7, 15, 10, 30, 45, 123456)
        utc = self.typ.process_bind_param(local, None)
        back = self.typ.process_result_value(utc, None)
        self.assertEqual(local, back)

    def test_round_trip_dst_fallback(self):
        """Fall-back ambiguous time round-trips correctly (CST interpretation)."""
        utc = self.typ.process_bind_param(DST_FALLBACK_LOCAL, None)
        back = self.typ.process_result_value(utc, None)
        self.assertEqual(DST_FALLBACK_LOCAL, back)

    # ------------------------------------------------------------------
    # Offset sanity — keeps tests honest if DST rules ever change
    # ------------------------------------------------------------------

    def test_cdt_offset_is_minus_5(self):
        utc = self.typ.process_bind_param(CDT_LOCAL, None)
        offset_hours = int((utc - CDT_LOCAL).total_seconds() // 3600)
        self.assertEqual(5, offset_hours, "CDT should be UTC-5")

    def test_cst_offset_is_minus_6(self):
        utc = self.typ.process_bind_param(CST_LOCAL, None)
        offset_hours = int((utc - CST_LOCAL).total_seconds() // 3600)
        self.assertEqual(6, offset_hours, "CST should be UTC-6")

    # ------------------------------------------------------------------
    # Invalid input — date (not datetime) must be rejected
    # ------------------------------------------------------------------

    def test_bind_date_only_raises(self):
        """A bare date object has no tzinfo attribute and must not be passed to process_bind_param."""
        with self.assertRaises((AttributeError, TypeError)):
            self.typ.process_bind_param(date(2026, 4, 20), None)
