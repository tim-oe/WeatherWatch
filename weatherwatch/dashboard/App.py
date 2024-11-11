import logging
from pathlib import Path
from urllib.parse import quote

import dash_bootstrap_components as dbc
import dash_daq as daq
import flask
from conf.AppConfig import AppConfig
from conf.DashConfig import DashConfig
from conf.SensorConfig import SensorConfig
from dash import Dash, Input, Output, dcc, html
from dashboard.page.CameraPage import CameraPage
from dashboard.page.IndoorSensorPage import IndoorSensorPage
from dashboard.page.OutdoorSensorPage import OutdoorSensorPage
from dashboard.page.SystemPage import SystemPage
from furl import furl
from py_singleton import singleton


@singleton
class App:
    """
    dashboard application entry point
    https://dash.plotly.com/
    https://dash.plotly.com/dash-html-components
    https://dash.plotly.com/dash-core-components
    https://dash.plotly.com/dash-daq
    https://github.com/ucg8j/awesome-dash
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

    # TODO need to add ability to toggle
    # https://dash.plotly.com/dash-daq/darkthemeprovider
    ROOT_THEME = {
        "dark": True,
        "detail": "#007439",
        "primary": "#00DDEA",
        "secondary": "#6E6E6E",
    }

    def __init__(self):
        """
        ctor
        :param self: this
        """

        self._appConfig = AppConfig()
        self._dashConfig: DashConfig = self._appConfig.dashboard

        self._app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

        content = html.Div([dcc.Location(id="url"), self.sidebar(), 
                            html.Div(id="page-content", style=App.CONTENT_STYLE)])

        self._app.layout = html.Div(
            children=[daq.DarkThemeProvider(theme=App.ROOT_THEME, children=content)]
        )

        self._staticFolder = Path(__file__).parent.parent.parent / "static"

        logging.info("static folder: %s", self._staticFolder)

        self._app.callback(Output("page-content", "children"), [Input("url", "href")])(self.renderPageContent)

        self._app.server.route("/cam/<resource>")(self.serveCamImage)
        self._app.server.route("/vid/<resource>")(self.serveCamVid)
        self._app.server.route("/static/img/<resource>")(self.serveResImage)

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
                html.H6("Weather Watch"),
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
        try:
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
        except Exception:
            logging.exception("failed to render page %s", f)
            return self.serverError(f)

    def missingPageContent(self, f: furl) -> html.Div:
        return html.Div(
            [
                html.Center(html.H1(f"404: Not found {f}", className="text-danger")),
                html.Hr(),
                html.Center(html.Img(height=270, width=450, src="/static/img/error.jpg")),
            ]
        )

    def serverError(self, f: furl) -> html.Div:
        return html.Div(
            [
                html.Center(html.H1(f"500: server error {f}", className="text-danger")),
                html.Hr(),
                html.Center(html.Img(height=270, width=450, src="/static/img/error.jpg")),
            ]
        )

    def serveCamImage(self, resource):
        folder: Path = self._appConfig.camera.folder
        logging.debug(str(folder.resolve() / resource))
        return flask.send_from_directory(folder.resolve(), resource)

    def serveCamVid(self, resource):
        folder: Path = self._appConfig.timelapse.folder
        logging.debug(str(folder.resolve() / resource))
        return flask.send_from_directory(folder.resolve(), resource)

    def serveResImage(self, resource):
        return flask.send_from_directory(self._staticFolder / "img", resource)

    def run(self):
        self._app.run(host=self._dashConfig.host, 
                      port=self._dashConfig.port, 
                      debug=self._dashConfig.debug)
