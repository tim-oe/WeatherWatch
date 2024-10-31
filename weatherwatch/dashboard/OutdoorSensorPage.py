from datetime import date
from decimal import Decimal

import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import html
from dashboard.BasePage import BasePage
from dashboard.component.HumidityGauge import HumidityGauge
from dashboard.component.TempratureGauge import TempratureGauge
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
            ]
        )

    def rainGuage(self, rain: Decimal) -> daq.Tank:

        max: int = 25

        if rain > 25:
            factor: int = int(rain // 25)
            max = 25 * (factor + 1)

        return daq.Tank(
            max=max,
            min=0,
            width=100,
            scale={"interval": 5, "labelInterval": 1},
            label="total rainfall",
            value=round(rain, 1),
            showCurrentValue=True,
            units="mm",
        )
