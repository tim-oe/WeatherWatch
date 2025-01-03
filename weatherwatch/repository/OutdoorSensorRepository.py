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
    """
    outdoor sensor repo
    """

    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__(entity=OutdoorSensor)

    def find_latest(self) -> OutdoorSensor:
        """
        get the latest record
        :param self: this
        :return the latest record
        """
        session: Session = self._datastore.session
        try:
            val = session.query(OutdoorSensor).order_by(OutdoorSensor.read_time.desc()).first()
            return val
        finally:
            session.close()

    # pylint: disable=duplicate-code
    def find_greater_than_read_time(self, dt: datetime) -> List[OutdoorSensor]:
        """
        get records greater than the given date
        :param self: this
        :param dt: the lower bound date
        :return the list of records
        """
        session: Session = self._datastore.session
        try:
            return (
                session.query(OutdoorSensor).filter(OutdoorSensor.read_time > dt).order_by(OutdoorSensor.read_time.desc()).all()
            )
        finally:
            session.close()

    def get_days_rainfall(self, rain_date: date) -> Decimal:
        """
        get the total days rain fall
        :param self: this
        :param date: date to lookup rain fall
        theres an edge case of just after midnight where there will not be
        data for the current day yet
        """
        session: Session = self._datastore.session
        try:
            r: Row = (
                session.query(func.sum(OutdoorSensor.rain_delta_mm).label("total"))
                .filter(cast(OutdoorSensor.read_time, DATE) == rain_date)
                .group_by(cast(OutdoorSensor.read_time, DATE))
                .first()
            )
            if r is not None:
                return r.total

            return Decimal(0.0)
        finally:
            session.close()

    # pylint: disable=duplicate-code
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
                for v in session.query(OutdoorSensor).filter(cast(OutdoorSensor.read_time, DATE).between(from_date, to_date)):
                    f.write(f"{self.get_insert(v)};\n")
            finally:
                f.close()
                session.close()
