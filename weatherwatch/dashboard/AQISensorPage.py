import dash_bootstrap_components as dbc
from dashboard.BasePage import BasePage
from repository.AQISensorRepository import AQISensorRepository


class AQISensorPage(BasePage):
    """
    AQI sensor page
    """  # noqa

    PATH = "/aqisensor"

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._outdoorRepo: AQISensorRepository = AQISensorRepository()

        super().__init__()

    def content(self, **kwargs) -> dbc.Container:
        pass
