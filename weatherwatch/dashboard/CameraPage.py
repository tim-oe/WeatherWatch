import dash_bootstrap_components as dbc
from dash import html
from conf.CameraConfig import CameraConfig
from dashboard.BasePage import BasePage

from PIL import Image

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

        pImg = Image.open(self._cameraConfig.currentFile)

        return dbc.Container(
            children=dbc.Stack([
                html.center(html.H1("Current view")),
                html.Hr(),
                html.Img(src=pImg),
            ])
        )
