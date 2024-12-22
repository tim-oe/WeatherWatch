import dash_bootstrap_components as dbc
from dash import html
from dashboard.component.SystemResourceGauge import SystemResourceGauge
from dashboard.component.TempratureGauge import TempratureGauge
from dashboard.page.BasePage import BasePage
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
        self._pi_metrics_svc: PIMetricsSvc = PIMetricsSvc()

        super().__init__()

    def content(self, **kwargs) -> dbc.Container:
        """
        render page content
        :param self: this
        :param kwargs: additional arguments
        """

        data: PIMetrics = self._pi_metrics_svc.get_metrics()

        return dbc.Container(
            [
                dbc.Row(
                    children=dbc.Col(children=html.Center(html.H4(f" utime: {self._pi_metrics_svc.get_uptime()}"))),
                ),
                dbc.Row(children=dbc.Col(children=html.Hr())),
                dbc.Row(
                    [
                        dbc.Col([SystemResourceGauge("memory usage %", data.mem_percent, data.mem_available, data.mem_used)]),
                        dbc.Col([SystemResourceGauge("disk usage %", data.disk_percent, data.disk_available, data.disk_used)]),
                        dbc.Col(
                            [
                                TempratureGauge(
                                    label="cpu temp c",
                                    min_val=10,
                                    max_val=90,
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
