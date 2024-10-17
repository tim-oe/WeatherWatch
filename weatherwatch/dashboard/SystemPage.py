import dash_bootstrap_components as dbc
from dash import html
from dashboard.BasePage import BasePage
from dashboard.component.PercentGauge import PercentGauge
from dashboard.component.TempratureGauge import TempratureGauge
from entity.PIMetrics import PIMetrics
from svc.PIMetricsSvc import PIMetricsSvc


class SystemPage(BasePage):
    """
    system dash page
    """  # noqa

    PATH = "/System"

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._piMetricsSvc: PIMetricsSvc = PIMetricsSvc()

        super().__init__()

    def content(self, **kwargs) -> dbc.Container:
        data: PIMetrics = self._piMetricsSvc.getMetrics()

        return dbc.Container(
            [
                #dbc.Row(dbc.Col(html.Plaintext("Uptime: {0} days {1}:{2}:{3}".format(self._piMetricsSvc.getUptime())))),  # noqa
                dbc.Row(
                    [
                        dbc.Col([PercentGauge("memory usage %", data.mem_percent, data.mem_available, data.mem_used)]),
                        dbc.Col([PercentGauge("disk usage %", data.disk_percent, data.disk_available, data.disk_used)]),
                        dbc.Col(
                            [
                                TempratureGauge(
                                    label="cpu temp c",
                                    min=10,
                                    max=90,
                                    low=30,
                                    mid=50,
                                    high=70,
                                    value=data.cpu_temp_c,
                                    units="c",
                                )
                            ]
                        ),
                    ]
                ),
            ]
        )
