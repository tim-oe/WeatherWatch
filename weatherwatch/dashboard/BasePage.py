from abc import ABC, abstractmethod

from conf.AppConfig import AppConfig
from dash import html


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
    def content(self, **kwargs) -> html.Div: ...
