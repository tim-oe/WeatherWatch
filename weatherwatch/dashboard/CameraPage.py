from datetime import date, timedelta
from pathlib import Path

import dash_bootstrap_components as dbc
import dash_player as dp
from conf.CameraConfig import CameraConfig
from conf.TimelapseConfig import TimelapseConfig
from dash import html
from dashboard.BasePage import BasePage


class CameraPage(BasePage):
    """
    camera dash page
    https://community.plotly.com/t/how-to-embed-images-into-a-dash-app/61839
    https://stackoverflow.com/questions/68747552/how-to-show-a-local-image-in-an-interactive-dash-with-python
    """  # noqa

    PATH = "/Camera"

    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__()

        self._cameraConfig: CameraConfig = self._appConfig.camera
        self._timelapseConfig: TimelapseConfig = self._appConfig.timelapse

    def content(self, **kwargs) -> dbc.Container:

        currImage: Path = self._cameraConfig.currentFile

        d = date.today() - timedelta(days=1)
        stamp = d.strftime("%Y-%m-%d")

        return dbc.Container(
            children=[
                dbc.Row(
                    children=dbc.Col(children=html.Center(html.H1("Current view"))),
                ),
                dbc.Row(children=dbc.Col(children=html.Hr())),
                dbc.Row(children=html.Img(src=f"/cam/{currImage.name}")),
                dbc.Row(children=dbc.Col(children=html.Hr())),
                dbc.Row(
                    children=dbc.Col(
                        children=dp.DashPlayer(
                            id="player",
                            url=f"/vid/{stamp}{self._timelapseConfig.extension}",
                            controls=True,
                            width="100%",
                            height="750px",
                        ),
                    )
                ),
                # dbc.Row(children=dbc.Col(children=html.Video(src=f"/vid/{stamp}{self._timelapseConfig.extension}",controls=True))),
            ]
        )
