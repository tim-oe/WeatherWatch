from datetime import date, timedelta
from typing import List

import dash_bootstrap_components as dbc
from dash import html
from dashboard.component.BarometricPressureGauge import BarometricPressureGauge
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
        self._outdoorRepo: OutdoorSensorRepository = OutdoorSensorRepository()

        super().__init__()

    def content(self, **kwargs) -> dbc.Container:

        data: OutdoorSensor = self._outdoorRepo.findLatest()
        rainFail = self._outdoorRepo.getDaysRainfall(date.today())

        return dbc.Container(
            [
                dbc.Row(children=dbc.Col(html.Center(children=html.H4(f" read time: {data.read_time.isoformat()}")))),
                dbc.Row(children=dbc.Col(html.Hr())),
                dbc.Row(
                    align="stretch",
                    children=[
                        dbc.Col(
                            id="out-t-col",
                            children=TempratureGauge(
                                label="temprature",
                                min=-10,
                                max=120,
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
                            children=RainGauge(rainFail),
                        ),
                    ],
                ),
                dbc.Row(children=dbc.Col(html.Hr())),
                dbc.Row(children=[
                        dbc.Col(UVGauge(data.uv)),
                        dbc.Col(WindGauge(data.wind_avg_m_s, "wind ave")),
                        dbc.Col(WindGauge(data.wind_max_m_s, "wind gust"))
                ]),

                dbc.Row(children=dbc.Col(html.Hr())),
                dbc.Row(children=dbc.Col(html.Center(html.H2("Wind distribution for past 7 days")))),
                dbc.Row(children=dbc.Col(self.windCompass())),
            ]
        )

    def windCompass(self) -> WindCompass:
        d = date.today() - timedelta(days=7)

        data: List[OutdoorSensor] = self._outdoorRepo.findGreaterThanReadTime(d)

        return WindCompass(data)
