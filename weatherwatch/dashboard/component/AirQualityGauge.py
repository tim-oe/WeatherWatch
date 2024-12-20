import dash_bootstrap_components as dbc

# pylint: disable=not-callable
import dash_daq as daq


class AirQualityGauge(dbc.Container):
    """
    air quality gauge class
    https://dash.plotly.com/dash-daq/tank
    """

    def __init__(self, label: str, value: int, units: str = "ug/m3"):
        """
        ctor
        :param self: this
        """
        super().__init__(
            [
                daq.Tank(
                    max=50,
                    min=0,
                    width=100,
                    label=label,
                    value=value,
                    showCurrentValue=True,
                    scale={"interval": 5, "labelInterval": 2},
                    units=units,
                )
            ]
        )
