from decimal import Decimal

import dash_daq as daq
from dash import html


class RainGauge(html.Div):
    """
    humidity guage class
    https://dash.plotly.com/dash-daq/tank
    """

    BASE_SCALER: int = 25

    def __init__(self, rain: Decimal, units: str = "mm"):
        """
        ctor
        :param self: this
        :param rain: the rain ammount
        :param units: the rain units
        """
        factor: int = 1
        if rain > RainGauge.BASE_SCALER:
            factor = int(rain // RainGauge.BASE_SCALER)

        super().__init__(
            [
                daq.Tank(
                    max=25 * factor,
                    min=0,
                    width=100,
                    scale={"interval": 5 * factor, "labelInterval": factor},
                    label="total rainfall",
                    value=round(rain, 1),
                    showCurrentValue=True,
                    units=units,
                )
            ]
        )
