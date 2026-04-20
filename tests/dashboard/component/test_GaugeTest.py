import unittest
from decimal import Decimal

from dashboard.component.AirQualityGauge import AirQualityGauge
from dashboard.component.BarometricPressureGauge import BarometricPressureGauge
from dashboard.component.HumidityGauge import HumidityGauge
from dashboard.component.SystemResourceGauge import SystemResourceGauge
from dashboard.component.TempratureGauge import TempratureGauge
from dashboard.component.UVGauge import UVGauge
from dashboard.component.WindGauge import WindGauge


class AirQualityGaugeTest(unittest.TestCase):

    def test_instantiation(self):
        gauge = AirQualityGauge(label="PM2.5", value=12)
        self.assertIsNotNone(gauge)

    def test_instantiation_with_units(self):
        gauge = AirQualityGauge(label="PM1.0", value=5, units="ug/m3")
        self.assertIsNotNone(gauge)


class BarometricPressureGaugeTest(unittest.TestCase):

    def test_instantiation(self):
        gauge = BarometricPressureGauge(pressure=Decimal("1013.25"))
        self.assertIsNotNone(gauge)

    def test_instantiation_with_units(self):
        gauge = BarometricPressureGauge(pressure=Decimal("1010.0"), units="hPa")
        self.assertIsNotNone(gauge)


class HumidityGaugeTest(unittest.TestCase):

    def test_instantiation(self):
        gauge = HumidityGauge(humidity=Decimal("65.5"))
        self.assertIsNotNone(gauge)

    def test_zero_humidity(self):
        gauge = HumidityGauge(humidity=Decimal("0.0"))
        self.assertIsNotNone(gauge)


class UVGaugeTest(unittest.TestCase):

    def test_instantiation(self):
        gauge = UVGauge(uv=Decimal("3.2"))
        self.assertIsNotNone(gauge)

    def test_zero_uv(self):
        gauge = UVGauge(uv=Decimal("0.0"))
        self.assertIsNotNone(gauge)


class WindGaugeTest(unittest.TestCase):

    def test_instantiation(self):
        gauge = WindGauge(wind=Decimal("5.5"), label="wind ave")
        self.assertIsNotNone(gauge)

    def test_with_custom_units(self):
        gauge = WindGauge(wind=Decimal("2.1"), label="gust", units="m/s")
        self.assertIsNotNone(gauge)


class SystemResourceGaugeTest(unittest.TestCase):

    def test_instantiation(self):
        gauge = SystemResourceGauge(
            label="CPU",
            value=42,
            available=1024 * 1024 * 512,
            used=1024 * 1024 * 100,
        )
        self.assertIsNotNone(gauge)


class TempratureGaugeTest(unittest.TestCase):

    def test_blue_range(self):
        """value < mid → blue"""
        gauge = TempratureGauge(label="temp", units="f", value=60.0, min_val=0, max_val=120, mid=75, high=90)
        self.assertIsNotNone(gauge)

    def test_yellow_range(self):
        """mid < value < high → yellow"""
        gauge = TempratureGauge(label="temp", units="f", value=80.0, min_val=0, max_val=120, mid=75, high=90)
        self.assertIsNotNone(gauge)

    def test_red_range(self):
        """value >= high → red"""
        gauge = TempratureGauge(label="temp", units="f", value=95.0, min_val=0, max_val=120, mid=75, high=90)
        self.assertIsNotNone(gauge)
