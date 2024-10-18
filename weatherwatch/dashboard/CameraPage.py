from pathlib import Path

import dash_bootstrap_components as dbc
from conf.CameraConfig import CameraConfig
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

    def content(self, **kwargs) -> dbc.Container:

        currImage: Path = self._cameraConfig.currentFile

        return dbc.Container(
            children=dbc.Stack(
                [
                    html.Center(html.H1("Current view")),
                    html.Hr(),
                    html.Img(src=f"/camera/{currImage.name}"),
                ]
            )
        )
