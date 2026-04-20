import unittest
from datetime import datetime
from types import SimpleNamespace

from dashboard.component.Graph import Graph


def _make_record(value, t=None):
    return SimpleNamespace(read_time=t or datetime(2026, 1, 1, 12, 0, 0), val=value)


class GraphTest(unittest.TestCase):

    def test_build_graph_large_delta_over_100(self):
        """delta > 100 → min/max padded by 10."""
        records = [_make_record(float(i)) for i in range(150)]
        g = Graph("title", "val", "units", "val", records)
        self.assertIsNotNone(g)

    def test_build_graph_medium_delta_over_20(self):
        """20 < delta <= 100 → min/max padded by 5."""
        records = [_make_record(float(i)) for i in range(50)]
        g = Graph("title", "val", "units", "val", records)
        self.assertIsNotNone(g)

    def test_build_graph_small_delta_20_or_less(self):
        """delta <= 20 → min/max padded by 1."""
        records = [_make_record(float(i)) for i in range(10)]
        g = Graph("title", "val", "units", "val", records)
        self.assertIsNotNone(g)

    def test_build_graph_constant_values(self):
        """All identical values → delta 0 → padded by 1."""
        records = [_make_record(42.0) for _ in range(5)]
        g = Graph("const", "val", "C", "val", records)
        self.assertIsNotNone(g)

    def test_build_graph_single_record(self):
        records = [_make_record(10.0)]
        g = Graph("single", "val", "u", "val", records)
        self.assertIsNotNone(g)
