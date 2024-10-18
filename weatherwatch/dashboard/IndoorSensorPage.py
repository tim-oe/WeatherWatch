import dash_bootstrap_components as dbc
from conf.SensorConfig import SensorConfig
from dash import html
from dashboard.BasePage import BasePage
from dashboard.component.TempHumidityGauge import TempHumidityGauge
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
            [
                dbc.Row(
                    align="stretch",
                    children=dbc.Col(html.Center(children=html.H4(f" read time: {data.read_time.isoformat()}"))),
                ),
                dbc.Row(align="stretch", children=dbc.Col(html.Hr())),
                dbc.Row(dbc.Col(TempHumidityGauge(data.temperature_f, data.humidity))),
            ]
        )
