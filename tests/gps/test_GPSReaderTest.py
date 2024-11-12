import unittest

from gps.DMSCoordinate import Ordinal
from gps.GPSData import GPSData
from gps.GPSReader import GPSReader

class GPSReaderTest(unittest.TestCase):
    def test(self):
        bs: GPSReader = GPSReader()
        data: GPSData = bs.read()
        
        self.assertIsNotNone(data)
        self.assertEqual(Ordinal.NORTH, data.latitudeDMS.ordinal)
        self.assertEqual(Ordinal.WEST, data.longitudeDMS.ordinal)
        print(f"{data}")
        print(f"latitudeDMS {data.latitudeDMS}")
        print(f"longitudeDMS {data.longitudeDMS}")
