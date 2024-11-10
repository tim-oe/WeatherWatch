import dash_bootstrap_components as dbc
from dashboard.page.BasePage import BasePage
from repository.AQISensorRepository import AQISensorRepository


class AirQualityPage(BasePage):
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
