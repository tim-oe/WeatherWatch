from datetime import date, datetime
from typing import List

from conf.AppConfig import AppConfig
from entity.AQISensor import AQISensor
from py_singleton import singleton
from repository.BaseRepository import BaseRepository
from sqlalchemy import DATE, cast
from sqlalchemy.orm import Session

__all__ = ["AQISensorRepository"]


@singleton
class AQISensorRepository(BaseRepository[AQISensor]):
    """
    indoor sensor repo
    """

    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__(entity=AQISensor)
        self._ceiling: int = AppConfig().aqi.ceiling

    def find_latest(self) -> AQISensor:
        """
        get the latest record
        :param self: this
        :return the latest record
        """
        session: Session = self._datastore.session
        try:
            return session.query(AQISensor).order_by(AQISensor.read_time.desc()).first()
        finally:
            session.close()

    def find_greater_than_read_time(self, dt: datetime) -> List[AQISensor]:
        """
        get records greater than the given date
        :param self: this
        :param dt: the lower bound date
        :return the list of records
        """
        session: Session = self._datastore.session
        try:
            return session.query(AQISensor).filter(AQISensor.read_time > dt).order_by(AQISensor.read_time.desc()).all()
        finally:
            session.close()

    def backup(self, from_date: date, to_date: date, file_name: str):
        """
        generate backup file for a given data range
        :param self: this
        :param from_date: from date
        :param to_date: to date
        :param file_name: the backup file name
        """
        with open(file_name, "w", encoding="utf-8") as f:
            session: Session = self._datastore.session
            try:
                for v in session.query(AQISensor).filter(cast(AQISensor.read_time, DATE).between(from_date, to_date)):
                    f.write(f"{self.get_insert(v)};\n")
            finally:
                f.close()
                session.close()

    def clean(self):
        """
        clean records with readings outside of valid range
        delegates to the aqi_clean stored procedure
        :param self: this
        """
        self.exec(f"CALL aqi_clean({self._ceiling})")
