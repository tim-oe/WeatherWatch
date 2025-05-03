from datetime import date, timedelta
from typing import List

import dash_bootstrap_components as dbc
from conf.SensorConfig import SensorConfig
from dash import html
from dashboard.component.Graph import Graph
from dashboard.component.HumidityGauge import HumidityGauge
from dashboard.component.TempratureGauge import TempratureGauge
from dashboard.page.BasePage import BasePage
from entity.IndoorSensor import IndoorSensor
from repository.IndoorSensorRepository import IndoorSensorRepository


class IndoorSensorPage(BasePage):
    """
    indoor sensor dash page
    """  # noqa

    PATH = "/IndoorData"

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._indoor_repo: IndoorSensorRepository = IndoorSensorRepository()

        super().__init__()

    def content(self, **kwargs) -> dbc.Container:
        """
        render page content
        :param self: this
        :param kwargs: additional arguments
        """

        sensor: SensorConfig = self._app_config.get_sensor(kwargs["name"])

        data: IndoorSensor = self._indoor_repo.find_latest(sensor.channel)
        curr_date: str = data.read_time.strftime("%Y-%m-%d %H-%M-%S")

        min_temp = min(0, int(data.temperature_f) - 5)
        max_temp = max(100, int(data.temperature_f) + 5)

        d = date.today() - timedelta(days=7)
        seven_day: List[IndoorSensor] = self._indoor_repo.find_greater_than_read_time(sensor.channel, d)

        return dbc.Container(
            id=f"in-root-cont-{sensor.channel}",
            children=[
                dbc.Row(
                    children=dbc.Col(children=html.Center(html.H4(f"time: {curr_date}"))),
                ),
                dbc.Row(children=dbc.Col(children=html.Hr())),
                dbc.Row(
                    children=[
                        dbc.Col(
                            id="in-t-col",
                            children=TempratureGauge(
                                label="temprature",
                                min_val=min_temp,
                                max_val=max_temp,
                                mid=75,
                                high=90,
                                value=round(data.temperature_f, 1),
                                units="f",
                            ),
                        ),
                        dbc.Col(id="in-h-col", children=HumidityGauge(data.humidity)),
                    ]
                ),
                dbc.Row(children=dbc.Col(html.Hr())),
                dbc.Row(children=dbc.Col(html.Center(html.H2("7 day historical data")))),
                dbc.Row(children=dbc.Col(Graph("temprature", "temprature", "f", "temperature_f", data=seven_day))),
                dbc.Row(children=dbc.Col(Graph("humidity", "humidity", "%", "humidity", data=seven_day))),
            ],
        )
