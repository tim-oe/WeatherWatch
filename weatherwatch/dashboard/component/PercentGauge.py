import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import html


class PercentGauge(html.Div):
    """
    percent based guage class
    https://dash.plotly.com/dash-daq/gauge
    """

    def __init__(self, label: str, value: int, available, used):
        """
        ctor
        :param self: this
        """
        super().__init__(
            [
                daq.Gauge(
                    label=label,
                    value=value,
                    theme="darkly",
                    color={"gradient": True, "ranges": {"green": [0, 50], "yellow": [50, 85], "red": [85, 100]}},
                    max=100,
                    showCurrentValue=True,
                    units="%",
                ),
                dbc.Row([dbc.Col([html.Plaintext(children="available")]), dbc.Col([html.Plaintext(children=available)])]),
                dbc.Row([dbc.Col([html.Plaintext(children="used")]), dbc.Col([html.Plaintext(children=used)])]),
            ]
        )
