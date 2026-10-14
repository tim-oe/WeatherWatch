from abc import ABC, abstractmethod

import dash_bootstrap_components as dbc
from conf.AppConfig import AppConfig
from dash import html


class BasePage(ABC):
    """
    base dash page for common functionality
    https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/
    """  # noqa

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._app_config = AppConfig()

    def unavailable(self) -> dbc.Container:
        """
        render an empty state when the database cannot be read
        :param self: this
        :return: the container
        """
        return dbc.Container([dbc.Row(dbc.Col(html.H4("weather data unavailable")))])

    @abstractmethod
    def content(self, **kwargs) -> dbc.Container:
        """
        render page content
        :param self: this
        :param kwargs: additional arguments
        """
