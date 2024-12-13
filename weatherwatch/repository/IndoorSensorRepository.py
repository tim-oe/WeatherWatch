from datetime import date, datetime
from typing import List

from entity.IndoorSensor import IndoorSensor
from py_singleton import singleton
from repository.BaseRepository import BaseRepository
from sqlalchemy import DATE, and_, cast
from sqlalchemy.orm import Session

__all__ = ["IndoorSensorRepository"]


@singleton
class IndoorSensorRepository(BaseRepository[IndoorSensor]):

    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__(entity=IndoorSensor)

    def findLatest(self, c: int) -> IndoorSensor:
        session: Session = self._datastore.session
        try:
            return session.query(IndoorSensor).filter_by(channel=c).order_by(IndoorSensor.read_time.desc()).first()
        finally:
            session.close()

    def findGreaterThanReadTime(self, channel: int, dt: datetime) -> List[IndoorSensor]:
        session: Session = self._datastore.session
        try:
            return (
                session.query(IndoorSensor)
                .filter(and_(IndoorSensor.channel == channel, IndoorSensor.read_time > dt))
                .order_by(IndoorSensor.read_time.desc())
                .all()
            )
        finally:
            session.close()

    def backup(self, from_date: date, to_date: date, file_name: str):
        with open(file_name, "w", encoding="utf-8") as f:
            session: Session = self._datastore.session
            try:
                for v in session.query(IndoorSensor).filter(cast(IndoorSensor.read_time, DATE).between(from_date, to_date)):
                    f.write(f"{self.get_insert(v)};\n")
            finally:
                f.close()
                session.close()
