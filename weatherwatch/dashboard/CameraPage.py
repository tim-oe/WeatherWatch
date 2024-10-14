from dash import html

from dashboard.BasePage import BasePage


class CameraPage(BasePage):
    """
    system dash page    
    """  # noqa

    PATH='/Camera' 

    def __init__(self):
        """
        ctor
        :param self: this
        """

    def content(self, **kwargs) -> html.Div:
        return html.Div(
            [
                html.H1("Camera Page"),
                html.Hr(),
                html.P("TBD..."),
            ])
