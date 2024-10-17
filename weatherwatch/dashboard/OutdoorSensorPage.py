import dash_bootstrap_components as dbc
from dash import html
import dash_daq as daq
from dashboard.BasePage import BasePage
from dashboard.component.TempHumidityGauge import TempHumidityGauge
from entity.OutdoorSensor import OutdoorSensor
from repository.OutdoorSensorRepository import OutdoorSensorRepository


class OutdoorSensorPage(BasePage):
    """
    system dash page
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

        return dbc.Container(
            [
                dbc.Row(align="stretch", children=dbc.Col(html.Center(children=html.H4(f" read time: {data.read_time.isoformat()}")))),
                dbc.Row(align="stretch", children=dbc.Col(html.Hr())),
                dbc.Row(id="out-row", align="stretch", children=[
                    dbc.Col(id="out-th-col", align="stretch", width=True, children=TempHumidityGauge(data.temperature_f, data.humidity)),
                    # https://dash.plotly.com/dash-daq/tank
                    dbc.Col(id="out-p-col", align="stretch", children=daq.Tank(
                        max=1050,
                        min=950,
                        width=100,
                        label="air pressure",
                        value=round(data.pressure, 1),
                        showCurrentValue=True,
                        units='hPa',
                    ))
                    ]),
                # TODO wind
            ]
        )
