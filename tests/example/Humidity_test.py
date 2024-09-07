import unittest

from src.sensor.Humidity import Humidity


class HumidityTest(unittest.TestCase):
    def test(self):
        h: Humidity = Humidity()

        val: str = str(h.read())

        print(val)

        self.assertRegex(val, "[\d.]+")
