from datetime import date, timedelta
from typing import List

import dash_bootstrap_components as dbc
from dash import html
from dashboard.component.AirQualityGauge import AirQualityGauge
from dashboard.component.Graph import Graph
from dashboard.page.BasePage import BasePage
from entity.AQISensor import AQISensor
from repository.AQISensorRepository import AQISensorRepository


class AirQualityPage(BasePage):
    """
    AQI sensor page
    """  # noqa

    PATH = "/aqisensor"

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._aqiRepo: AQISensorRepository = AQISensorRepository()

        super().__init__()

    def content(self, **kwargs) -> dbc.Container:
        data: AQISensor = self._aqiRepo.findLatest()
        currDate: str = data.read_time.strftime("%Y-%m-%d %H-%M-%S")

        d = date.today() - timedelta(days=7)
        sevenDay: List[AQISensor] = self._aqiRepo.findGreaterThanReadTime(d)

        return dbc.Container(
            [
                dbc.Row(children=dbc.Col(html.Center(children=html.H4(f"time: {currDate}")))),
                dbc.Row(children=dbc.Col(html.Hr())),
                dbc.Row(
                    align="stretch",
                    children=[
                        dbc.Col(
                            id="out-pm1-col", children=AirQualityGauge("PM1.0 atm concentration", data.pm_1_0_conctrt_atmosph)
                        ),
                        dbc.Col(
                            id="out-pm2.5-col", children=AirQualityGauge("PM2.5 atm concentration", data.pm_2_5_conctrt_atmosph)
                        ),
                        dbc.Col(
                            id="out-pm10-col", children=AirQualityGauge("PM1.0 atm concentration", data.pm_10_conctrt_atmosph)
                        ),
                    ],
                ),
                dbc.Row(children=dbc.Col(html.Hr())),
                dbc.Row(children=dbc.Col(html.Center(html.H2("7 day historical data")))),
                dbc.Row(
                    children=dbc.Col(
                        Graph(
                            "PM1.0 atmospheric concentration",
                            "PM1.0 atm conc",
                            "ug/m3",
                            "pm_1_0_conctrt_atmosph",
                            data=sevenDay,
                        )
                    )
                ),
                dbc.Row(
                    children=dbc.Col(
                        Graph(
                            "PM2.5 atmospheric concentration",
                            "PM2.5 atm conc",
                            "ug/m3",
                            "pm_2_5_conctrt_atmosph",
                            data=sevenDay,
                        )
                    )
                ),
                dbc.Row(
                    children=dbc.Col(
                        Graph(
                            "PM10 atmospheric concentration", "PM10 atm conc", "ug/m3", "pm_10_conctrt_atmosph", data=sevenDay
                        )
                    )
                ),
            ]
        )
