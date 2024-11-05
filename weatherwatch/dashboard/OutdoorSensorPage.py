from datetime import date, timedelta
from decimal import Decimal
from typing import List

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_daq as daq
from dash import html
from dashboard.BasePage import BasePage
from dashboard.component.HumidityGauge import HumidityGauge
from dashboard.component.TempratureGauge import TempratureGauge
from dashboard.component.WindCompass import WindCompass
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
                        dbc.Col(
                            id="out-p-col",
                            children=daq.Tank(
                                max=1050,
                                min=950,
                                width=100,
                                label="air pressure",
                                value=round(data.pressure, 1),
                                showCurrentValue=True,
                                units="hPa",
                            ),
                        ),
                        dbc.Col(
                            id="out-r-col",
                            children=self.rainGuage(rainFail),
                        ),
                    ],
                ),
                dbc.Row(children=dbc.Col(html.Hr())),
                dbc.Row(children=dbc.Col(html.Center(html.H2("Wind distribution for past 7 days")))),
                dbc.Row(children=dbc.Col(self.windCompass())),
            ]
        )

    def rainGuage(self, rain: Decimal) -> daq.Tank:

        max: int = 25

        factor: int = 1        
        if rain > 25:
            factor = int(rain // 25)

        return daq.Tank(
            max=25 * (factor + 1),
            min=0,
            width=100,
            scale={"interval": 5 * factor, "labelInterval": 1 + (factor - 1)},
            label="total rainfall",
            value=round(rain, 1),
            showCurrentValue=True,
            units="mm",
        )

    def windCompass(self) -> WindCompass:
        d = date.today() - timedelta(days=7)

        data: List[OutdoorSensor] = self._outdoorRepo.findGreaterThanReadTime(d)
        
        return WindCompass(data)