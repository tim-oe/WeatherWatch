import dash_daq as daq
from dash import html


class TempratureGauge(html.Div):
    """
    temprature based thermometer guage class
    https://dash.plotly.com/dash-daq/thermometer
    """

    def __init__(self, label: str, units: str, value: float, min: int, max: int, low: int, mid: int, high: int):
        """
        ctor
        :param self: this
        """
        color = "blue"
        if value > mid and value < high:
            color = "yellow"
        elif value >= high:
            color = "red"

        super().__init__(
            [
                daq.Thermometer(
                    label=label,
                    min=min,
                    max=max,
                    className="dark-theme-control",
                    color=color,
                    value=value,
                    showCurrentValue=True,
                    units=units,
                )
            ]
        )
