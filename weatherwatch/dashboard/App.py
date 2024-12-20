from pathlib import Path
from urllib.parse import quote

import dash_bootstrap_components as dbc

# pylint: disable=not-callable
import dash_daq as daq
import flask
from conf.AppConfig import AppConfig
from conf.DashConfig import DashConfig
from conf.SensorConfig import SensorConfig
from dash import Dash, Input, Output, dcc, html
from dashboard.page.AirQualityPage import AirQualityPage
from dashboard.page.CameraPage import CameraPage
from dashboard.page.IndoorSensorPage import IndoorSensorPage
from dashboard.page.OutdoorSensorPage import OutdoorSensorPage
from dashboard.page.SystemPage import SystemPage
from flask import Flask
from furl import furl
from py_singleton import singleton
from util.Logger import logger
from waitress import serve


@logger
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

        self._app_config = AppConfig()
        self._dash_config: DashConfig = self._app_config.dashboard

        self._server = Flask(__name__)

        self._app = Dash(__name__, server=self._server, external_stylesheets=[dbc.themes.DARKLY])

        content = html.Div([dcc.Location(id="url"), self.sidebar(), html.Div(id="page-content", style=App.CONTENT_STYLE)])

        self._app.layout = html.Div(children=[daq.DarkThemeProvider(theme=App.ROOT_THEME, children=content)])

        self._static_folder = Path(__file__).parent.parent.parent / "static"

        self.logger.info("static folder: %s", self._static_folder)

        self._app.callback(Output("page-content", "children"), [Input("url", "href")])(self.render_page_content)

        # self._server.route("/")(self._app.index())
        self._server.route("/cam/<resource>")(self.serve_cam_image)
        self._server.route("/vid/<resource>")(self.serve_cam_vid)
        self._server.route("/static/img/<resource>")(self.serve_res_image)

    def sidebar(self) -> html.Div:

        links = []

        links.append(dbc.NavLink("system", id=SystemPage.__name__, href=SystemPage.PATH, active="exact"))
        links.append(dbc.NavLink("camera", id=CameraPage.__name__, href=CameraPage.PATH, active="exact"))

        if self._app_config.aqi.enable:
            links.append(dbc.NavLink("air quality", id=AirQualityPage.__name__, href=AirQualityPage.PATH, active="exact"))

        s: SensorConfig
        for s in self._app_config.sensors:
            links.append(
                dbc.NavLink(s.name, id=quote(s.name), href=f"/{quote(s.data_class)}?name={quote(s.name)}", active="exact")
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

    def render_page_content(self, href: str):
        """
        render page based on href request
        :param self: this
        :param href: href request
        """
        try:
            f: furl = furl(href)
            self.logger.debug("request [%s]", f)
            match f.path:
                case App.ROOT_PATH:
                    return SystemPage().content()
                case SystemPage.PATH:
                    return SystemPage().content()
                case CameraPage.PATH:
                    return CameraPage().content()
                case AirQualityPage.PATH:
                    return AirQualityPage().content()
                case IndoorSensorPage.PATH:
                    return IndoorSensorPage().content(name=f.args["name"])
                case OutdoorSensorPage.PATH:
                    return OutdoorSensorPage().content(name=f.args["name"])
                case _:
                    self.logger.error(" unhandled request [%s]", f)
                    return self.missing_page_content(f)
        except Exception:
            self.logger.exception("failed to render page %s", f)
            return self.server_error(f)

    def missing_page_content(self, f: furl) -> html.Div:
        """
        render the missing page content
        :param self: this
        :param href: f the request details
        :return: the missing page detail div
        """
        return html.Div(
            [
                html.Center(html.H1(f"404: Not found {f}", className="text-danger")),
                html.Hr(),
                html.Center(html.Img(height=270, width=450, src="/static/img/error.jpg")),
            ]
        )

    def server_error(self, f: furl) -> html.Div:
        """
        render the server error
        :param self: this
        :param href: f the request details
        :return: the server error detail div
        """
        return html.Div(
            [
                html.Center(html.H1(f"500: server error {f}", className="text-danger")),
                html.Hr(),
                html.Center(html.Img(height=270, width=450, src="/static/img/error.jpg")),
            ]
        )

    def serve_cam_image(self, resource):
        """
        render the camera image
        :param self: this
        :param href: resource image resource
        """
        folder: Path = self._app_config.camera.folder
        self.logger.debug(str(folder.resolve() / resource))
        return flask.send_from_directory(folder.resolve(), resource)

    def serve_cam_vid(self, resource):
        """
        render the camera video
        :param self: this
        :param href: resource video resource
        """
        folder: Path = self._app_config.timelapse.folder
        self.logger.debug(str(folder.resolve() / resource))
        return flask.send_from_directory(folder.resolve(), resource)

    def serve_res_image(self, resource):
        """
        render the image resource
        :param self: this
        :param href: resource image resource
        """
        return flask.send_from_directory(self._static_folder / "img", resource)

    def run(self):
        """
        run the dash app
        :param self: this
        """
        if self._dash_config.debug:
            self._app.run(host=self._dash_config.host, port=self._dash_config.port, debug=self._dash_config.debug)
        else:
            serve(self._server, host=self._dash_config.host, port=self._dash_config.port)
