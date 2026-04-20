import unittest
from types import SimpleNamespace

from dashboard.component.WindCompass import WindCompass


def _make_outdoor(wind_avg_m_s=0.0, wind_dir_deg=0.0):
    return SimpleNamespace(wind_avg_m_s=wind_avg_m_s, wind_dir_deg=wind_dir_deg)


def _bare_compass(data=None):
    """Create a WindCompass instance without triggering dbc.Container.__init__."""
    obj = object.__new__(WindCompass)
    obj._data = data if data is not None else []
    return obj


class WindCompassGetCardinalBucketTest(unittest.TestCase):

    def setUp(self):
        self.c = _bare_compass()

    def test_north_exact(self):
        self.assertEqual(0, self.c.get_cardinal_bucket(0.0))

    def test_north_high_wrap(self):
        self.assertEqual(0, self.c.get_cardinal_bucket(350.0))

    def test_north_upper_boundary(self):
        self.assertEqual(0, self.c.get_cardinal_bucket(337.5))

    def test_northeast(self):
        self.assertEqual(1, self.c.get_cardinal_bucket(45.0))

    def test_east(self):
        self.assertEqual(2, self.c.get_cardinal_bucket(90.0))

    def test_southeast(self):
        self.assertEqual(3, self.c.get_cardinal_bucket(135.0))

    def test_south(self):
        self.assertEqual(4, self.c.get_cardinal_bucket(180.0))

    def test_southwest(self):
        self.assertEqual(5, self.c.get_cardinal_bucket(225.0))

    def test_west(self):
        self.assertEqual(6, self.c.get_cardinal_bucket(270.0))

    def test_northwest(self):
        self.assertEqual(7, self.c.get_cardinal_bucket(315.0))


class WindCompassGetSpeedBucketTest(unittest.TestCase):

    def setUp(self):
        self.c = _bare_compass()

    def test_calm(self):
        self.assertEqual(0, self.c.get_speed_bucket(0.0))

    def test_light(self):
        self.assertEqual(1, self.c.get_speed_bucket(1.5))

    def test_moderate(self):
        self.assertEqual(2, self.c.get_speed_bucket(3.0))

    def test_fresh(self):
        self.assertEqual(3, self.c.get_speed_bucket(6.0))

    def test_strong(self):
        self.assertEqual(4, self.c.get_speed_bucket(9.0))

    def test_storm(self):
        self.assertEqual(5, self.c.get_speed_bucket(15.0))

    def test_boundary_less_than_1(self):
        self.assertEqual(0, self.c.get_speed_bucket(0.99))

    def test_boundary_exactly_11(self):
        self.assertEqual(5, self.c.get_speed_bucket(11.0))


class WindCompassUnitConversionTest(unittest.TestCase):

    def setUp(self):
        self.c = _bare_compass()

    def test_convert_wind_units_metric(self):
        self.assertEqual(5.0, self.c.convert_wind_units(5.0))

    def test_get_wind_scale_metric(self):
        self.assertEqual(" m/s", self.c.get_wind_scale())

    def test_get_wind_speed_converted_zero(self):
        self.assertEqual("0.0", self.c.get_wind_speed_converted(0.0))

    def test_get_wind_speed_converted_nonzero(self):
        self.assertEqual("5.0", self.c.get_wind_speed_converted(5.0))


class WindCompassProcessWindDataTest(unittest.TestCase):

    def test_empty_data_returns_zero_buckets(self):
        c = _bare_compass(data=[])
        df = c.process_wind_data()
        self.assertEqual(6, len(df))
        for bucket in df:
            self.assertEqual([0, 0, 0, 0, 0, 0, 0, 0], bucket)

    def test_single_record_100_percent_in_bucket(self):
        data = [_make_outdoor(wind_avg_m_s=0.5, wind_dir_deg=0.0)]  # speed 0, cardinal 0
        c = _bare_compass(data=data)
        df = c.process_wind_data()
        self.assertEqual(100.0, df[0][0])

    def test_two_records_splits_50_50(self):
        data = [
            _make_outdoor(wind_avg_m_s=0.5, wind_dir_deg=0.0),   # speed 0, cardinal 0
            _make_outdoor(wind_avg_m_s=5.0, wind_dir_deg=90.0),  # speed 3, cardinal 2
        ]
        c = _bare_compass(data=data)
        df = c.process_wind_data()
        self.assertAlmostEqual(50.0, df[0][0])
        self.assertAlmostEqual(50.0, df[3][2])

    def test_all_cardinal_directions_covered(self):
        directions = [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0]
        data = [_make_outdoor(wind_avg_m_s=0.5, wind_dir_deg=d) for d in directions]
        c = _bare_compass(data=data)
        df = c.process_wind_data()
        for i in range(8):
            self.assertAlmostEqual(100.0 / 8, df[0][i], places=1)


class WindCompassFigureTest(unittest.TestCase):

    def test_fig_compass_rose_returns_figure(self):
        import plotly.graph_objs as go
        data = [_make_outdoor(wind_avg_m_s=i * 0.5, wind_dir_deg=i * 45.0 % 360)
                for i in range(8)]
        c = _bare_compass(data=data)
        fig = c.fig_compass_rose()
        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(6, len(fig.data))

    def test_init_with_data_creates_component(self):
        data = [_make_outdoor(wind_avg_m_s=1.0, wind_dir_deg=180.0)]
        compass = WindCompass(data)
        self.assertIsNotNone(compass)


class WindCompassInvalidCardinalTest(unittest.TestCase):

    def test_nan_direction_raises_value_error(self):
        """NaN direction leaves cardinal_bucket == -1 → ValueError on line 192."""
        c = _bare_compass()
        with self.assertRaises(ValueError):
            c.get_cardinal_bucket(float("nan"))
