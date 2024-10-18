import dash_bootstrap_components as dbc
import dash_daq as daq
from dashboard.component.TempratureGauge import TempratureGauge


class TempHumidityGauge(dbc.Container):
    """
    temprature and humidity guage class
    https://dash.plotly.com/dash-daq/gauge
    """

    def __init__(self, temprature: float, humidity: int):
        """
        ctor
        :param self: this
        """
        super().__init__(
            fluid=True,
            children=dbc.Row(
                id="th-row",
                align="stretch",
                children=[
                    dbc.Col(
                        id="th-t-col",
                        align="stretch",
                        width=True,
                        children=TempratureGauge(
                            label="temprature",
                            min=-10,
                            max=120,
                            low=32,
                            mid=75,
                            high=90,
                            value=round(temprature, 1),
                            units="f",
                        ),
                    ),
                    dbc.Col(
                        id="th-h-col",
                        align="stretch",
                        width=True,
                        children=daq.Gauge(
                            label="humidity",
                            value=round(humidity, 1),
                            color={"gradient": True, "ranges": {"green": [0, 50], "yellow": [50, 85], "red": [85, 100]}},
                            max=100,
                            showCurrentValue=True,
                            units="%",
                            className="dark-theme-control",
                        ),
                    ),
                ],
            ),
        )
