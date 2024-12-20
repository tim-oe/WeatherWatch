import dash_bootstrap_components as dbc

# pylint: disable=not-callable
import dash_daq as daq


class TempratureGauge(dbc.Container):
    """
    temprature based thermometer guage class
    https://dash.plotly.com/dash-daq/thermometer
    """

    def __init__(self, label: str, units: str, value: float, min: int, max: int, mid: int, high: int, size: int = 100):
        """
        ctor
        :param self: this
        """
        color = "blue"
        if value > mid and value < high:
            color = "yellow"
        elif value >= high:
            color = "red"

        scale = {"start": min, "interval": 10, "labelInterval": 2, "custom": {}}

        # add current instead of bottom
        scale["custom"][f"{round(value,1)}"] = f"<----{round(value,1)}"

        super().__init__(
            [
                daq.Thermometer(
                    label=label, min=min, max=max, color=color, value=value, showCurrentValue=False, units=units, scale=scale
                )
            ]
        )
