from decimal import Decimal

import dash_bootstrap_components as dbc

# pylint: disable=not-callable
import dash_daq as daq


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
                    color={
                        "gradient": True,
                        "ranges": {"yellow": [0, 40], "green": [40, 70], "red": [70, 100]},
                    },
                    max=100,
                    showCurrentValue=True,
                    units="%",
                )
            ]
        )
