import unittest
from src.sensor.Loudness import Loudness


class HumidityTest(unittest.TestCase):
    def test(self):
        l: Loudness = Loudness()

        val: str = str(l.read())

        print(val)

        self.assertRegex(val, "\d+")
