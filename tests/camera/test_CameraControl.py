import unittest

from camera.CameraControls import CameraControls


class CameraControlsTest(unittest.TestCase):

    def assert_controls(self, lux: float, expected_exposure: int, expected_gain: float):
        controls = CameraControls(lux)

        self.assertFalse(controls.AeEnable)
        self.assertTrue(controls.AwbEnable)
        self.assertEqual(controls.ExposureTime, expected_exposure)
        self.assertEqual(controls.AnalogueGain, expected_gain)

    def assert_image_controls(self, lux: float, expected_brightness: float, expected_contrast: float, expected_saturation: float):
        controls = CameraControls(lux)
        self.assertEqual(controls.Brightness, expected_brightness)
        self.assertEqual(controls.Contrast, expected_contrast)
        self.assertEqual(controls.Saturation, expected_saturation)

    def test_bright_daylight_10000_lux(self):
        self.assert_controls(10000.0, 500, 1.0)

    def test_overcast_1000_lux(self):
        self.assert_controls(1000.0, 2_000, 1.0)

    def test_indoor_bright_100_lux(self):
        self.assert_controls(100.0, 20_000, 1.0)

    def test_dim_indoor_10_lux(self):
        self.assert_controls(10.0, 80_000, 1.0)

    def test_dusk_5_lux(self):
        self.assert_controls(5.0, 400_000, 2.0)

    def test_dusk_1_lux(self):
        self.assert_controls(1.0, 1_000_000, 4.0)

    def test_night_floor_0_5_lux(self):
        self.assert_controls(0.5, 3_000_000, 4.0)

    def test_night_0_4_lux(self):
        self.assert_controls(0.4, 3_277_293, 8.0)

    def test_moonlit_night_0_1_lux(self):
        self.assert_controls(0.1, 5_000_000, 8.0)

    def test_dark_night_0_05_lux(self):
        self.assert_controls(0.05, 6_505_149, 8.0)

    def test_dark_night_floor_0_01_lux(self):
        self.assert_controls(0.01, 10_000_000, 8.0)

    def test_image_controls_daylight(self):
        self.assert_image_controls(100.0, 0.0, 1.0, 1.0)

    def test_image_controls_twilight(self):
        self.assert_image_controls(5.0, 0.05, 1.1, 1.05)

    def test_image_controls_night(self):
        self.assert_image_controls(0.2, 0.1, 1.2, 1.1)

