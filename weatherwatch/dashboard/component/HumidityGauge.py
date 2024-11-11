from decimal import Decimal

import dash_daq as daq
import dash_bootstrap_components as dbc

class HumidityGauge(dbc.Container):
    """
    humidity guage class
    https://dash.plotly.com/dash-daq/gauge
    """

    def __init__(self, humidity: Decimal):
        """
        ctor
        :param self: this
        """
        super().__init__(
            [
                daq.Gauge(
                    label="humidity",
                    value=round(humidity, 1),
                    color={"gradient": True, "ranges": {"green": [0, 50], "yellow": [50, 85], "red": [85, 100]}},
                    max=100,
                    showCurrentValue=True,
                    units="%",
                    #className="dark-theme-control",
                )
            ]
        )
