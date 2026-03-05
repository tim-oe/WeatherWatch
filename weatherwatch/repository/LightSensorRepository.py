from datetime import date, datetime
from typing import List

from entity.LightSensor import LightSensor
from py_singleton import singleton
from repository.BaseRepository import BaseRepository
from sqlalchemy import DATE, cast
from sqlalchemy.orm import Session

__all__ = ["LightSensorRepository"]


@singleton
class LightSensorRepository(BaseRepository[LightSensor]):
    """
    light sensor repo
    """

    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__(entity=LightSensor)

    def find_latest(self) -> LightSensor:
        """
        get the latest record
        :param self: this
        :return the latest record
        """
        session: Session = self._datastore.session
        try:
            return session.query(LightSensor).order_by(LightSensor.read_time.desc()).first()
        finally:
            session.close()

    def find_greater_than_read_time(self, dt: datetime) -> List[LightSensor]:
        """
        get records greater than the given date
        :param self: this
        :param dt: the lower bound date
        :return the list of records
        """
        session: Session = self._datastore.session
        try:
            return session.query(LightSensor).filter(LightSensor.read_time > dt).order_by(LightSensor.read_time.desc()).all()
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
                for v in session.query(LightSensor).filter(cast(LightSensor.read_time, DATE).between(from_date, to_date)):
                    f.write(f"{self.get_insert(v)};\n")
            finally:
                f.close()
                session.close()
