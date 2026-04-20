import unittest

from entity.AQISensor import AQISensor, PM_FIELDS


def _make_aqi(**kwargs) -> AQISensor:
    """Create an AQISensor instance with specified PM field values."""
    s = AQISensor()
    for field in PM_FIELDS:
        setattr(s, field, kwargs.get(field, 0))
    return s


class AQISensorFudgeTest(unittest.TestCase):
    """Tests for AQISensor.fudge() — outlier replacement with neighbour average."""

    def test_fudge_both_neighbors_averages_values(self):
        current = _make_aqi(**{f: 200 for f in PM_FIELDS})
        prev = _make_aqi(**{f: 10 for f in PM_FIELDS})
        nxt = _make_aqi(**{f: 20 for f in PM_FIELDS})
        current.fudge(prev, nxt, ceiling=100)
        for field in PM_FIELDS:
            self.assertEqual(15, getattr(current, field))

    def test_fudge_prev_only_uses_prev(self):
        current = _make_aqi(**{f: 200 for f in PM_FIELDS})
        prev = _make_aqi(**{f: 30 for f in PM_FIELDS})
        current.fudge(prev, None, ceiling=100)
        for field in PM_FIELDS:
            self.assertEqual(30, getattr(current, field))

    def test_fudge_nxt_only_uses_nxt(self):
        current = _make_aqi(**{f: 200 for f in PM_FIELDS})
        nxt = _make_aqi(**{f: 40 for f in PM_FIELDS})
        current.fudge(None, nxt, ceiling=100)
        for field in PM_FIELDS:
            self.assertEqual(40, getattr(current, field))

    def test_fudge_below_ceiling_no_change(self):
        current = _make_aqi(**{f: 50 for f in PM_FIELDS})
        prev = _make_aqi(**{f: 10 for f in PM_FIELDS})
        nxt = _make_aqi(**{f: 20 for f in PM_FIELDS})
        current.fudge(prev, nxt, ceiling=100)
        for field in PM_FIELDS:
            self.assertEqual(50, getattr(current, field))

    def test_fudge_at_ceiling_no_change(self):
        """A value exactly equal to ceiling is not treated as an outlier."""
        current = _make_aqi(**{f: 100 for f in PM_FIELDS})
        prev = _make_aqi(**{f: 5 for f in PM_FIELDS})
        nxt = _make_aqi(**{f: 5 for f in PM_FIELDS})
        current.fudge(prev, nxt, ceiling=100)
        for field in PM_FIELDS:
            self.assertEqual(100, getattr(current, field))

    def test_fudge_neither_neighbor_no_change(self):
        """When both neighbors are None the outlier field is unchanged."""
        current = _make_aqi(**{f: 500 for f in PM_FIELDS})
        current.fudge(None, None, ceiling=100)
        for field in PM_FIELDS:
            self.assertEqual(500, getattr(current, field))

    def test_fudge_mixed_fields(self):
        """Only fields exceeding ceiling are replaced; others remain."""
        current = _make_aqi(**{f: (200 if i % 2 == 0 else 10) for i, f in enumerate(PM_FIELDS)})
        prev = _make_aqi(**{f: 6 for f in PM_FIELDS})
        nxt = _make_aqi(**{f: 4 for f in PM_FIELDS})
        current.fudge(prev, nxt, ceiling=100)
        for i, field in enumerate(PM_FIELDS):
            if i % 2 == 0:
                self.assertEqual(5, getattr(current, field))
            else:
                self.assertEqual(10, getattr(current, field))
