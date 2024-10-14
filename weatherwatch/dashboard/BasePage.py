from dash import html

from conf.AppConfig import AppConfig

from abc import ABC, abstractmethod

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
    def content(self, **kwargs) -> html.Div:
        ...