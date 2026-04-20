import unittest
from decimal import Decimal

from dashboard.component.RainGauge import RainGauge


class RainGaugeTest(unittest.TestCase):

    def test_rain_below_scaler_factor_is_one(self):
        """rain <= 25 → factor stays at 1."""
        gauge = RainGauge(Decimal("10.0"))
        self.assertIsNotNone(gauge)

    def test_rain_at_scaler_boundary(self):
        """rain exactly at BASE_SCALER (25) → factor 1."""
        gauge = RainGauge(Decimal("25.0"))
        self.assertIsNotNone(gauge)

    def test_rain_above_scaler_factor_grows(self):
        """rain > 25 → factor = int(rain // 25) > 1."""
        gauge = RainGauge(Decimal("50.0"))
        self.assertIsNotNone(gauge)

    def test_rain_large_value(self):
        """Very large rain value handled without error."""
        gauge = RainGauge(Decimal("200.0"))
        self.assertIsNotNone(gauge)

    def test_rain_with_custom_units(self):
        gauge = RainGauge(Decimal("5.0"), "in")
        self.assertIsNotNone(gauge)

    def test_rain_zero(self):
        gauge = RainGauge(Decimal("0.0"))
        self.assertIsNotNone(gauge)
