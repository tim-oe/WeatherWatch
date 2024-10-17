from dash import html
from dashboard.BasePage import BasePage


class CameraPage(BasePage):
    """
    camera dash page
    https://stackoverflow.com/questions/68747552/how-to-show-a-local-image-in-an-interactive-dash-with-python
    """  # noqa

    PATH = "/Camera"

    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__()

    def content(self, **kwargs) -> html.Div:
        return html.Div(
            [
                html.H1("Camera Page"),
                html.Hr(),
                html.P("TBD..."),
            ]
        )
