from decimal import Decimal

import dash_bootstrap_components as dbc

# pylint: disable=not-callable
import dash_daq as daq


class WindGauge(dbc.Container):
    """
    wind guage class
    https://dash.plotly.com/dash-daq/tank
    """

    def __init__(self, wind: Decimal, label: str, units: str = "mm/s"):
        """
        ctor
        :param self: this
        :param wind: the wind ammount
        :param units: the wind units
        """

        super().__init__(
            [
                daq.Tank(
                    max=40,
                    min=0,
                    width=100,
                    scale={"interval": 5, "labelInterval": 1},
                    label=label,
                    value=round(wind, 1),
                    showCurrentValue=True,
                    units=units,
                )
            ]
        )
