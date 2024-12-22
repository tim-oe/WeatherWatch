from datetime import datetime, timedelta
import unittest

from dashboard.App import App
from tests.repository.BaseRepositoryTest import BaseRespositoryTest
import dash
from abc import ABC
import time

 
class BaseDashboardTest(unittest.TestCase, ABC):
    """
    base test class for dashboard testing
    """ 

    def setup_method(self, method):
        print(f"!!!calling setup {method.__name__}")

        self.app: App = App()
        self.assertIsNotNone(self.app)        

        BaseRespositoryTest.load(datetime.now() + timedelta(days=8))

        self._dash_app = self.dash_app()

    @classmethod
    def teardown_class(self):
        BaseRespositoryTest.teardown_db()


    def dash_app(self):
        app: App = App()
        yield dash.testing.application_runners.ThreadedRunner().run(app)
