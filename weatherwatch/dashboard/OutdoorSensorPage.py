from dash import html
from dashboard.BasePage import BasePage


class OutdoorSensorPage(BasePage):
    """
    system dash page
    """  # noqa

    PATH = "/OutdoorData"

    def __init__(self):
        """
        ctor
        :param self: this
        """

    def content(self, **kwargs) -> html.Div:
        return html.Div(
            [
                html.H1("Outdoor Sensor Page"),
                html.Hr(),
                html.P(f"name={kwargs['name']}"),
            ]
        )
