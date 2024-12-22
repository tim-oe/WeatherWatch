import dash_bootstrap_components as dbc

# pylint: disable=not-callable
import dash_daq as daq


class TempratureGauge(dbc.Container):
    """
    temprature based thermometer guage class
    https://dash.plotly.com/dash-daq/thermometer
    """

    def __init__(self, label: str, units: str, value: float, min_val: int, max_val: int, mid: int, high: int):
        """
        ctor
        :param self: this
        """
        color = "blue"
        if value >= high:
            color = "red"
        elif value > mid:
            color = "yellow"

        scale = {"start": min_val, "interval": 10, "labelInterval": 2, "custom": {}}

        # add current instead of bottom
        scale["custom"][f"{round(value,1)}"] = f"<----{round(value,1)}"

        super().__init__(
            [
                daq.Thermometer(
                    label=label,
                    min=min_val,
                    max=max_val,
                    color=color,
                    value=value,
                    showCurrentValue=False,
                    units=units,
                    scale=scale,
                )
            ]
        )
