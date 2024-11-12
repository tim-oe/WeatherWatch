
from abc import ABC, abstractmethod
import unittest

from repository.BaseRepository import BaseRepository

class BaseRespositoryTest(unittest.TestCase, ABC):
    """
    TODO this is not working unless session is handled external to repo.
    https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
    """  # noqa

    @abstractmethod
    def getRepo(self) -> BaseRepository:
        ...
        
    def setup_method(self, test_method):
        repo: BaseRepository = self.getRepo()
        repo.exec(f'truncate {repo.entity.__table__}')

    @classmethod
    def teardown_class(self):
        repo: BaseRepository = self.getRepo(self)
        repo.exec(f'truncate {repo.entity.__table__}')
        
        # self.getRepo(self)._datastore.stop()
        # self.trans.rollback()
        # self.session.close()
        # self.connection.close()
        