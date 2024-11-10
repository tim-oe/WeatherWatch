from decimal import Decimal

import dash_daq as daq
from dash import html


class BarometricPressureGauge(html.Div):
    """
    humidity guage class
    https://dash.plotly.com/dash-daq/tank
    https://science.howstuffworks.com/nature/climate-weather/meteorological-instruments/barometric-pressure.htm
    https://learn.weatherstem.com/modules/learn/lessons/125/18.html
    """

    def __init__(self, pressure: Decimal, units: str = "hPa"):
        """
        ctor
        :param self: this
        """
        super().__init__(
            [
                daq.Tank(
                    max=1050,
                    min=950,
                    width=100,
                    label="air pressure",
                    value=round(pressure, 1),
                    showCurrentValue=True,
                    units=units,
                )
            ]
        )
