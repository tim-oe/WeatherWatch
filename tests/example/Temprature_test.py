import unittest
from src.sensor.Temprature import Temprature


class TempratureTest(unittest.TestCase):
    def test(self):
        t: Temprature = Temprature()

        val: str = str(t.read())

        print(val)

        self.assertRegex(val, "[\d.]+")
