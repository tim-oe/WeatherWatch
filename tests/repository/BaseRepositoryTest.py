
from abc import ABC, abstractmethod
from datetime import date, timedelta
from pathlib import Path
import shutil
import tempfile
import unittest
from pyutil import filereplace

from conf.AppConfig import AppConfig
from conf.DatabaseConfig import DatabaseConfig
from repository.AQISensorRepository import AQISensorRepository
from repository.BaseRepository import BaseRepository
from repository.IndoorSensorRepository import IndoorSensorRepository
from repository.OutdoorSensorRepository import OutdoorSensorRepository

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
        Path("test.sql").unlink(missing_ok=True)
        
        # TODO transactions.
        # self.getRepo(self)._datastore.stop()
        # self.trans.rollback()
        # self.session.close()
        # self.connection.close()

    @staticmethod
    def createSql(table_name: str, d: date, repo):
        for x in range(1, 5):
            stamp = d.strftime("%Y-%m-%d")
            src = f"tests/data/db/{x}_{table_name}.sql"
            tgt = f"{stamp}_{table_name}.sql"

            print(tgt)

            outFile: Path = Path(tempfile.gettempdir() / Path(tgt))

            shutil.copy(Path(src), outFile)
            filereplace(outFile.resolve(), "__YYYY_MM_DD__", stamp)
            repo.exec_file(outFile.resolve())
            outFile.unlink()

            d = d + timedelta(days=1)

    @staticmethod
    def load(start_date: date):
        dbConfig: DatabaseConfig = AppConfig().database
        if dbConfig.production:
            raise Exception("DO NOT RUN ON PROD!!!!")

        indoorRepo: IndoorSensorRepository = IndoorSensorRepository()
        indoorRepo.exec(f"truncate {indoorRepo.entity.__table__}")

        outdoorRepo: OutdoorSensorRepository = OutdoorSensorRepository()
        outdoorRepo.exec(f"truncate {outdoorRepo.entity.__table__}")

        aqiRepo: AQISensorRepository = AQISensorRepository()
        aqiRepo.exec(f"truncate {aqiRepo.entity.__table__}")

        BaseRespositoryTest.createSql("outdoor_sensor", start_date - timedelta(days=7), outdoorRepo)
        BaseRespositoryTest.createSql("outdoor_sensor", start_date - timedelta(days=3), outdoorRepo)

        BaseRespositoryTest.createSql("indoor_sensor", start_date - timedelta(days=7), indoorRepo)
        BaseRespositoryTest.createSql("indoor_sensor", start_date - timedelta(days=3), indoorRepo)

        BaseRespositoryTest.createSql("aqi_sensor", start_date - timedelta(days=7), aqiRepo)
        BaseRespositoryTest.createSql("aqi_sensor", start_date - timedelta(days=3), aqiRepo)

        outdoorRepo.exec_file("tests/data/db/finalize.sql")        