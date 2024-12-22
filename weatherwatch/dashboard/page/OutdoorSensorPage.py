from datetime import date, timedelta
from typing import List

import dash_bootstrap_components as dbc
from dash import html
from dashboard.component.BarometricPressureGauge import BarometricPressureGauge
from dashboard.component.Graph import Graph
from dashboard.component.HumidityGauge import HumidityGauge
from dashboard.component.RainGauge import RainGauge
from dashboard.component.TempratureGauge import TempratureGauge
from dashboard.component.UVGauge import UVGauge
from dashboard.component.WindCompass import WindCompass
from dashboard.component.WindGauge import WindGauge
from dashboard.page.BasePage import BasePage
from entity.OutdoorSensor import OutdoorSensor
from repository.OutdoorSensorRepository import OutdoorSensorRepository


class OutdoorSensorPage(BasePage):
    """
    Outdoor sensor page
    https://dash.plotly.com/dash-daq/tank
    """  # noqa

    PATH = "/OutdoorData"

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._outdoor_repo: OutdoorSensorRepository = OutdoorSensorRepository()

        super().__init__()

    def content(self, **kwargs) -> dbc.Container:
        """
        render page content
        :param self: this
        :param kwargs: additional arguments
        """

        data: OutdoorSensor = self._outdoor_repo.find_latest()
        curr_date: str = data.read_time.strftime("%Y-%m-%d %H-%M-%S")

        rain_fail = self._outdoor_repo.get_days_rainfall(date.today())
        # for lazy testing...
        # rainFail = self._outdoorRepo.getDaysRainfall(date.today() - timedelta(days=3))

        d = date.today() - timedelta(days=7)
        seven_day: List[OutdoorSensor] = self._outdoor_repo.find_greater_than_read_time(d)

        return dbc.Container(
            [
                dbc.Row(children=dbc.Col(html.Center(children=html.H4(f"time: {curr_date}")))),
                dbc.Row(children=dbc.Col(html.Hr())),
                dbc.Row(
                    align="stretch",
                    children=[
                        dbc.Col(
                            id="out-t-col",
                            children=TempratureGauge(
                                label="temprature",
                                min_val=-10,
                                max_val=120,
                                mid=75,
                                high=90,
                                value=round(data.temperature_f, 1),
                                units="f",
                            ),
                        ),
                        dbc.Col(id="out-h-col", children=HumidityGauge(data.humidity)),
                        dbc.Col(id="out-p-col", children=BarometricPressureGauge(data.pressure)),
                        dbc.Col(
                            id="out-r-col",
                            children=RainGauge(rain_fail),
                        ),
                    ],
                ),
                dbc.Row(children=dbc.Col(html.Hr())),
                dbc.Row(
                    children=[
                        dbc.Col(UVGauge(data.uv)),
                        dbc.Col(WindGauge(data.wind_avg_m_s, "wind ave")),
                        dbc.Col(WindGauge(data.wind_max_m_s, "wind gust")),
                    ]
                ),
                dbc.Row(children=dbc.Col(html.Hr())),
                dbc.Row(children=dbc.Col(html.Center(html.H2("7 day historical data")))),
                dbc.Row(children=dbc.Col(WindCompass(seven_day))),
                dbc.Row(children=dbc.Col(Graph("temprature", "temprature", "c", "temperature_f", data=seven_day))),
                dbc.Row(children=dbc.Col(Graph("humidity", "humidity", "%", "humidity", data=seven_day))),
                dbc.Row(children=dbc.Col(Graph("pressure", "pressure", "hPa", "pressure", data=seven_day))),
                dbc.Row(children=dbc.Col(Graph("uv", "uv", "index", "uv", data=seven_day))),
                dbc.Row(children=dbc.Col(Graph("sunlight", "sunlight", "lux", "light_lux", data=seven_day))),
            ]
        )
