from dash import html
from dashboard.BasePage import BasePage


class IndoorSensorPage(BasePage):
    """
    system dash page
    """  # noqa

    PATH = "/IndoorData"

    def __init__(self):
        """
        ctor
        :param self: this
        """

    def content(self, **kwargs) -> html.Div:
        return html.Div(
            [
                html.H1("Indoor Sensor Page"),
                html.Hr(),
                html.P(f"name={kwargs['name']}"),
            ]
        )
