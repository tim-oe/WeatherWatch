from abc import ABC, abstractmethod

import dash_bootstrap_components as dbc
from conf.AppConfig import AppConfig


class BasePage(ABC):
    """
    base dash page for common functionality
    """  # noqa

    def __init__(self):
        """
        ctor
        :param self: this
        """

        self._appConfig = AppConfig()

    @abstractmethod
    def content(self, **kwargs) -> dbc.Container: ...
