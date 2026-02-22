from datetime import date, datetime
from typing import List, Optional

from conf.AppConfig import AppConfig
from entity.AQISensor import AQISensor
from py_singleton import singleton
from repository.BaseRepository import BaseRepository
from sqlalchemy import DATE, cast, or_
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

    def _find_previous_valid(self, session: Session, record_id: int) -> Optional[AQISensor]:
        """
        find the nearest previous record where all PM fields are within range
        :param self: this
        :param session: the db session
        :param record_id: the current record id
        :return: the nearest previous valid record, or None
        """
        return (
            session.query(AQISensor)
            .filter(
                AQISensor.id < record_id,
                AQISensor.pm_1_0_conctrt_std <= self._ceiling,
                AQISensor.pm_2_5_conctrt_std <= self._ceiling,
                AQISensor.pm_10_conctrt_std <= self._ceiling,
                AQISensor.pm_1_0_conctrt_atmosph <= self._ceiling,
                AQISensor.pm_2_5_conctrt_atmosph <= self._ceiling,
                AQISensor.pm_10_conctrt_atmosph <= self._ceiling,
            )
            .order_by(AQISensor.id.desc())
            .first()
        )

    def _find_next_valid(self, session: Session, record_id: int) -> Optional[AQISensor]:
        """
        find the nearest next record where all PM fields are within range
        :param self: this
        :param session: the db session
        :param record_id: the current record id
        :return: the nearest next valid record, or None
        """
        return (
            session.query(AQISensor)
            .filter(
                AQISensor.id > record_id,
                AQISensor.pm_1_0_conctrt_std <= self._ceiling,
                AQISensor.pm_2_5_conctrt_std <= self._ceiling,
                AQISensor.pm_10_conctrt_std <= self._ceiling,
                AQISensor.pm_1_0_conctrt_atmosph <= self._ceiling,
                AQISensor.pm_2_5_conctrt_atmosph <= self._ceiling,
                AQISensor.pm_10_conctrt_atmosph <= self._ceiling,
            )
            .order_by(AQISensor.id.asc())
            .first()
        )

    def clean(self, start_date: date, end_date: date):
        """
        clean records with readings outside of valid range within the given date range
        :param self: this
        :param start_date: the start date
        :param end_date: the end date
        """
        session: Session = self._datastore.session
        try:
            for d in (
                session.query(AQISensor)
                .filter(
                    cast(AQISensor.read_time, DATE).between(start_date, end_date),
                    or_(
                        AQISensor.pm_1_0_conctrt_std > self._ceiling,
                        AQISensor.pm_2_5_conctrt_std > self._ceiling,
                        AQISensor.pm_10_conctrt_std > self._ceiling,
                        AQISensor.pm_1_0_conctrt_atmosph > self._ceiling,
                        AQISensor.pm_2_5_conctrt_atmosph > self._ceiling,
                        AQISensor.pm_10_conctrt_atmosph > self._ceiling,
                    ),
                )
                .order_by(AQISensor.id.asc())
                .all()
            ):
                prev: Optional[AQISensor] = self._find_previous_valid(session, d.id)
                nxt: Optional[AQISensor] = self._find_next_valid(session, d.id)
                d.fudge(prev, nxt, self._ceiling)
                session.commit()
        finally:
            session.close()
