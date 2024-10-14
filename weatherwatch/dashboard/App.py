import logging
from conf.AppConfig import AppConfig
from conf.DashConfig import DashConfig

from py_singleton import singleton

from dash import Dash, html

import dash_bootstrap_components as dbc


@singleton
class App:

    """
    dashboard application entry point
    https://dash.plotly.com/
    """  # noqa

    def __init__(self):
        """
        ctor
        :param self: this
        """

        self._dashConfig: DashConfig = AppConfig().dashboard

        logging.basicConfig(level=logging.WARNING)
        
        self._app = Dash(__name__,external_stylesheets=[dbc.themes.DARKLY])

        self._app.layout = [html.H1(children='Weather Watch', style={'textAlign':'center'}),]

    def run(self):
            self._app.run(
        host=self._dashConfig.host,
        port=self._dashConfig.port,
        debug=True)