from decimal import Decimal

import dash_bootstrap_components as dbc
import dash_daq as daq


class BarometricPressureGauge(dbc.Container):
    """
    barometric pressure guage class
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
