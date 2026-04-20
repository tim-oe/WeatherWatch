import unittest

from gps.DMSCoordinate import DMSCoordinate, Ordinal
from gps.GPSData import GPSData
from gps.GPSReader import GPSReader


class GPSReaderTest(unittest.TestCase):
    def test(self):
        bs: GPSReader = GPSReader()
        data: GPSData = bs.read()

        self.assertIsNotNone(data)
        self.assertEqual(Ordinal.NORTH, data.latitude_dms.ordinal)
        self.assertEqual(Ordinal.WEST, data.longitude_dms.ordinal)
        print(f"{data}")
        print(f"latitudeDMS {data.latitude_dms}")
        print(f"longitudeDMS {data.longitude_dms}")


class DMSCoordinateTest(unittest.TestCase):
    """Unit tests for DMSCoordinate — no hardware required."""

    def test_north(self):
        c = DMSCoordinate(dd=43.6532, is_lat=True)
        self.assertEqual(Ordinal.NORTH, c.ordinal)

    def test_south(self):
        c = DMSCoordinate(dd=-33.8688, is_lat=True)
        self.assertEqual(Ordinal.SOUTH, c.ordinal)

    def test_east(self):
        c = DMSCoordinate(dd=151.2093, is_lat=False)
        self.assertEqual(Ordinal.EAST, c.ordinal)

    def test_west(self):
        c = DMSCoordinate(dd=-79.3832, is_lat=False)
        self.assertEqual(Ordinal.WEST, c.ordinal)

    def test_degrees_property(self):
        c = DMSCoordinate(dd=43.6532, is_lat=True)
        self.assertEqual(43.0, c.degrees)

    def test_minutes_property(self):
        c = DMSCoordinate(dd=43.6532, is_lat=True)
        self.assertGreater(c.minutes, 0)

    def test_seconds_property(self):
        c = DMSCoordinate(dd=43.6532, is_lat=True)
        self.assertGreaterEqual(c.seconds, 0)


class GPSDataTest(unittest.TestCase):
    """Unit tests for GPSData — no hardware required."""

    def test_latitude_getter(self):
        d = GPSData(latitude=43.6532, longitude=-79.3832, altitude=76.0)
        self.assertEqual(43.6532, d.latitude)

    def test_longitude_getter(self):
        d = GPSData(latitude=43.6532, longitude=-79.3832, altitude=76.0)
        self.assertEqual(-79.3832, d.longitude)

    def test_altitude_getter(self):
        d = GPSData(latitude=43.6532, longitude=-79.3832, altitude=76.0)
        self.assertEqual(76.0, d.altitude)

    def test_latitude_setter(self):
        d = GPSData()
        d.latitude = 51.5074
        self.assertEqual(51.5074, d.latitude)

    def test_longitude_setter(self):
        d = GPSData()
        d.longitude = -0.1278
        self.assertEqual(-0.1278, d.longitude)

    def test_altitude_setter(self):
        d = GPSData()
        d.altitude = 35.0
        self.assertEqual(35.0, d.altitude)
