import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import html
from hurry.filesize import size


class SystemResourceGauge(dbc.Container):
    """
    this is for system resources like memory and disk space
    https://dash.plotly.com/dash-daq/gauge
    """

    CONTENT_STYLE = {
        "padding": "0px 0px 0px 50px",
    }

    def __init__(self, label: str, value: int, available, used):
        """
        ctor
        :param self: this
        """
        super().__init__(
            fluid=True,
            children=[
                dbc.Row(
                    dbc.Col(
                        daq.Gauge(
                            label=label,
                            value=value,
                            color={
                                "gradient": True,
                                "ranges": {"green": [0, 50], "yellow": [50, 85], "red": [85, 100]},
                            },
                            max=100,
                            showCurrentValue=True,
                            units="%",
                            className="dark-theme-control",
                        )
                    ),
                    align="center",
                ),
                dbc.Row(
                    style=SystemResourceGauge.CONTENT_STYLE,
                    children=[
                        dbc.Col(align="center", width=True, children=[html.Plaintext(children="available")]),
                        dbc.Col([html.Plaintext(children=size(available))]),
                    ],
                    align="center",
                ),
                dbc.Row(
                    style=SystemResourceGauge.CONTENT_STYLE,
                    children=[
                        dbc.Col(align="center", width=True, children=[html.Plaintext(children="used")]),
                        dbc.Col([html.Plaintext(children=size(used))]),
                    ],
                    align="center",
                ),
            ],
        )
