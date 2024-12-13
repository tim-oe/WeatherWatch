from datetime import date, datetime
from decimal import Decimal
from typing import List

from entity.OutdoorSensor import OutdoorSensor
from py_singleton import singleton
from repository.BaseRepository import BaseRepository
from sqlalchemy import DATE, Row, cast, func
from sqlalchemy.orm import Session

__all__ = ["OutdoorSensorRepository"]


@singleton
class OutdoorSensorRepository(BaseRepository[OutdoorSensor]):

    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__(entity=OutdoorSensor)

    def findLatest(self) -> OutdoorSensor:
        session: Session = self._datastore.session
        try:
            val = session.query(OutdoorSensor).order_by(OutdoorSensor.read_time.desc()).first()
            return val
        finally:
            session.close()

    def findGreaterThanReadTime(self, dt: datetime) -> List[OutdoorSensor]:
        session: Session = self._datastore.session
        try:
            return (
                session.query(OutdoorSensor).filter(OutdoorSensor.read_time > dt).order_by(OutdoorSensor.read_time.desc()).all()
            )
        finally:
            session.close()

    def getDaysRainfall(self, date: date) -> Decimal:
        """
        theres an edge case of just after midnight where there will not be
        data for the current day yet
        """
        session: Session = self._datastore.session
        try:
            r: Row = (
                session.query(func.sum(OutdoorSensor.rain_delta_mm).label("total"))
                .filter(cast(OutdoorSensor.read_time, DATE) == date)
                .group_by(cast(OutdoorSensor.read_time, DATE))
                .first()
            )
            if r is not None:
                return r.total
            else:
                return Decimal(0.0)
        finally:
            session.close()

    def backup(self, from_date: date, to_date: date, file_name: str):
        with open(file_name, "w", encoding="utf-8") as f:
            session: Session = self._datastore.session
            try:
                for v in session.query(OutdoorSensor).filter(cast(OutdoorSensor.read_time, DATE).between(from_date, to_date)):
                    f.write(f"{self.get_insert(v)};\n")
            finally:
                f.close()
                session.close()
