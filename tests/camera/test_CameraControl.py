import unittest

from camera.CameraControls import CameraControls


class CameraControlsTest(unittest.TestCase):

    def assert_controls(self, lux: float, expected_exposure: int, expected_gain: float):
        controls = CameraControls(lux)

        self.assertFalse(controls.AeEnable)
        self.assertTrue(controls.AwbEnable)
        self.assertEqual(controls.ExposureTime, expected_exposure)
        self.assertEqual(controls.AnalogueGain, expected_gain)

    def test_bright_daylight_10000_lux(self):
        self.assert_controls(10000.0, 500, 1.0)

    def test_overcast_1000_lux(self):
        self.assert_controls(1000.0, 2_000, 1.0)

    def test_indoor_bright_100_lux(self):
        self.assert_controls(100.0, 20_000, 1.0)

    def test_dim_indoor_10_lux(self):
        self.assert_controls(10.0, 80_000, 1.0)

    def test_dusk_1_lux(self):
        self.assert_controls(1.0, 400_000, 2.0)

    def test_twilight_0_1_lux(self):
        self.assert_controls(0.1, 1_000_000, 4.0)

    def test_night_0_01_lux(self):
        self.assert_controls(0.01, 3_000_000, 8.0)

    def test_night_floor_0_001_lux(self):
        self.assert_controls(0.001, 3_000_000, 8.0)
