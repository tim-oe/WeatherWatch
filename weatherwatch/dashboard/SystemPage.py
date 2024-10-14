from dash import html
from dashboard.BasePage import BasePage


class SystemPage(BasePage):
    """
    system dash page    
    """  # noqa

    PATH='/System' 

    def __init__(self):
        """
        ctor
        :param self: this
        """

    def content(self, **kwargs) -> html.Div:
        return html.Div(
            [
                html.H1("System Page"),
                html.Hr(),
                html.P("TBD..."),
            ])
