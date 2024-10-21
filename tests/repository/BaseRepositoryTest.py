
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
        
    @classmethod
    def setup_class(self): 
        # TODO need to get transactions working...
        # self.rds: DataStore = self.getRepo(self)._datastore
        # self.connection = self.rds.connection
        # self.trans = self.connection.begin()
        # self.session = Session(bind=self.connection)

        # repo: BaseRepository = self.getRepo(self)

        # repo._datastore = Mock()
        # repo._datastore.session = self.session
        # repo._datastore.connection = self.connection

        # self.patcher1 = patch("repository.DataStore", repo._datastore)
        # self.patcher1.start()

        repo: BaseRepository = self.getRepo(self)
        repo.exec(f'truncate {repo.entity.__table__}')

    @classmethod
    def teardown_class(self):
        repo: BaseRepository = self.getRepo(self)
        repo.exec(f'truncate {repo.entity.__table__}')
        
        # self.getRepo(self)._datastore.stop()
        # self.trans.rollback()
        # self.session.close()
        # self.connection.close()
        