import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import html
from dashboard.BasePage import BasePage
from dashboard.component.PercentGauge import PercentGauge
from entity.PIMetrics import PIMetrics
from svc.PIMetricsSvc import PIMetricsSvc


class SystemPage(BasePage):
    """
    system dash page
    https://dash.plotly.com/dash-daq/thermometer
    """  # noqa

    PATH = "/System"

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._piMetricsSvc: PIMetricsSvc = PIMetricsSvc()

    def content(self, **kwargs) -> html.Div:
        data: PIMetrics = self._piMetricsSvc.getMetrics()

        return html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col([PercentGauge("memory usage %", data.mem_percent, data.mem_available, data.mem_used)]),
                        dbc.Col([PercentGauge("disk usage %", data.disk_percent, data.disk_available, data.disk_used)]),
                        dbc.Col([self.cpuTemp(data)]),
                    ]
                )
            ]
        )

    def cpuTemp(self, data: PIMetrics) -> daq.Thermometer:

        color = "blue"
        if data.cpu_temp_c >= 30 and data.cpu_temp_c < 60:
            color = "yellow"
        elif data.cpu_temp_c >= 60:
            color = "red"

        return daq.Thermometer(
            label="cpu temp",
            min=10,
            max=80,
            className="dark-theme-control",
            color=color,
            value=data.cpu_temp_c,
            showCurrentValue=True,
            units="C",
        )
