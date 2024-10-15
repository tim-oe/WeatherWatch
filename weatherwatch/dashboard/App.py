import logging
from urllib.parse import quote

import dash_bootstrap_components as dbc
from conf.AppConfig import AppConfig
from conf.DashConfig import DashConfig
from conf.SensorConfig import SensorConfig
from dash import Dash, Input, Output, dcc, html
from dashboard.CameraPage import CameraPage
from dashboard.IndoorSensorPage import IndoorSensorPage
from dashboard.OutdoorSensorPage import OutdoorSensorPage
from dashboard.SystemPage import SystemPage
from furl import furl
from py_singleton import singleton


@singleton
class App:
    """
    dashboard application entry point
    https://dash.plotly.com/
    https://dash-bootstrap-components.opensource.faculty.ai/examples/simple-sidebar/page-2#sourceCode

    """  # noqa

    ROOT_PATH = "/"

    # the style arguments for the sidebar. We use position:fixed and a fixed width
    # https://medium.com/@simurai/sizing-web-components-8f433689736f
    # https://www.sitepoint.com/understanding-and-using-rem-units-in-css/
    # https://www.w3schools.com/colors/colors_shades.asp
    SIDEBAR_STYLE = {
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "14rem",
        "padding": "2rem 1rem",
        "background-color": "#606060",
    }

    # the styles for the main content position it to the right of the sidebar and
    # add some padding.
    CONTENT_STYLE = {
        "margin-left": "18rem",
        "margin-right": "2rem",
        "padding": "2rem 1rem",
    }

    def __init__(self):
        """
        ctor
        :param self: this
        """

        self._appConfig = AppConfig()
        self._dashConfig: DashConfig = self._appConfig.dashboard

        self._app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

        self._app.layout = html.Div(
            [dcc.Location(id="url"), self.sidebar(), html.Div(id="page-content", style=App.CONTENT_STYLE)]
        )

        self._app.callback(Output("page-content", "children"), [Input("url", "href")])(self.renderPageContent)

    def sidebar(self) -> html.Div:

        links = []

        links.append(dbc.NavLink("system", id=SystemPage.__name__, href=SystemPage.PATH, active="exact"))
        links.append(dbc.NavLink("camera", id=CameraPage.__name__, href=CameraPage.PATH, active="exact"))

        s: SensorConfig
        for s in self._appConfig.sensors:
            links.append(
                dbc.NavLink(s.name, id=quote(s.name), href=f"/{quote(s.dataClass)}?name={quote(s.name)}", active="exact")
            )

        return html.Div(
            [
                html.H5("Weather Watch"),
                html.Hr(),
                dbc.Nav(
                    links,
                    vertical=True,
                    pills=True,
                ),
            ],
            style=App.SIDEBAR_STYLE,
        )

    def renderPageContent(self, href: str):
        f: furl = furl(href)
        logging.debug("request [%s]", f)
        match f.path:
            case App.ROOT_PATH:
                return SystemPage().content()
            case SystemPage.PATH:
                return SystemPage().content()
            case CameraPage.PATH:
                return CameraPage().content()
            case IndoorSensorPage.PATH:
                return IndoorSensorPage().content(name=f.args["name"])
            case OutdoorSensorPage.PATH:
                return OutdoorSensorPage().content(name=f.args["name"])
            case _:
                logging.error(" unhandled request [%s]", f)
                return self.missingPageContent(f)

    def missingPageContent(self, f: furl) -> html.Div:
        return html.Div(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"request {f} was not recognised..."),
            ]
        )

    def run(self):
        self._app.run(host=self._dashConfig.host, port=self._dashConfig.port, debug=True)
