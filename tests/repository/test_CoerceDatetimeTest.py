import unittest
from datetime import date, datetime

from repository.BaseRepository import BaseRepository


class CoerceDatetimeTest(unittest.TestCase):
    """
    Unit tests for BaseRepository._coerce_to_datetime.

    This helper is the single place that knows the LocalToUTCDateTime type
    converter requires a datetime (not a bare date). All repository methods
    that accept a date-range argument call it before touching SQLAlchemy.
    """

    def test_date_is_promoted_to_midnight_datetime(self):
        d = date(2026, 4, 21)
        result = BaseRepository._coerce_to_datetime(d)
        self.assertEqual(datetime(2026, 4, 21, 0, 0, 0), result)

    def test_datetime_is_returned_unchanged(self):
        dt = datetime(2026, 4, 21, 14, 30, 0)
        result = BaseRepository._coerce_to_datetime(dt)
        self.assertEqual(dt, result)
        self.assertIs(dt, result)

    def test_datetime_with_microseconds_is_returned_unchanged(self):
        dt = datetime(2026, 4, 21, 14, 30, 0, 123456)
        result = BaseRepository._coerce_to_datetime(dt)
        self.assertEqual(dt, result)

    def test_result_is_always_datetime(self):
        self.assertIsInstance(BaseRepository._coerce_to_datetime(date(2026, 1, 1)), datetime)
        self.assertIsInstance(BaseRepository._coerce_to_datetime(datetime(2026, 1, 1)), datetime)

    def test_datetime_subclass_not_double_converted(self):
        """datetime is a subclass of date; it must not be treated as a bare date."""
        dt = datetime(2026, 4, 21, 10, 0, 0)
        result = BaseRepository._coerce_to_datetime(dt)
        self.assertEqual(dt.hour, result.hour, "datetime hour must be preserved, not zeroed")

    def test_promoted_date_has_zero_time_components(self):
        result = BaseRepository._coerce_to_datetime(date(2026, 6, 15))
        self.assertEqual(0, result.hour)
        self.assertEqual(0, result.minute)
        self.assertEqual(0, result.second)
        self.assertEqual(0, result.microsecond)
