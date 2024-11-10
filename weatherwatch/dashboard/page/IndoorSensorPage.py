import dash_bootstrap_components as dbc
from conf.SensorConfig import SensorConfig
from dash import html
from dashboard.component.HumidityGauge import HumidityGauge
from dashboard.component.TempratureGauge import TempratureGauge
from dashboard.page.BasePage import BasePage
from entity.IndoorSensor import IndoorSensor
from repository.IndoorSensorRepository import IndoorSensorRepository


class IndoorSensorPage(BasePage):
    """
    system dash page
    """  # noqa

    PATH = "/IndoorData"

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._indoorRepo: IndoorSensorRepository = IndoorSensorRepository()

        super().__init__()

    def content(self, **kwargs) -> dbc.Container:

        sensor: SensorConfig = self._appConfig.getSensor(kwargs["name"])

        data: IndoorSensor = self._indoorRepo.findLatest(sensor.channel)

        return dbc.Container(
            id="in-root-cont",
            children=[
                dbc.Row(
                    children=dbc.Col(children=html.Center(html.H4(f" read time: {data.read_time.isoformat()}"))),
                ),
                dbc.Row(children=dbc.Col(children=html.Hr())),
                dbc.Row(
                    children=[
                        dbc.Col(
                            id="in-t-col",
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
                        dbc.Col(id="in-h-col", children=HumidityGauge(data.humidity)),
                    ]
                ),
            ],
        )
