from datetime import date, datetime
from typing import List, Union

from conf.AppConfig import AppConfig
from entity.AQISensor import AQISensor
from py_singleton import singleton
from repository.BaseRepository import BaseRepository
from repository.db_read import db_read
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

    @db_read(default=None)
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

    @db_read(default=[])
    def find_greater_than_read_time(self, dt: Union[date, datetime]) -> List[AQISensor]:
        """
        get records greater than the given date
        :param self: this
        :param dt: the lower bound date (date or datetime; a bare date is treated as midnight)
        :return the list of records
        """
        session: Session = self._datastore.session
        try:
            return (
                session.query(AQISensor)
                .filter(AQISensor.read_time > self._coerce_to_datetime(dt))
                .order_by(AQISensor.read_time.desc())
                .all()
            )
        finally:
            session.close()

    def clean(self):
        """
        clean records with readings outside of valid range
        delegates to the aqi_clean stored procedure
        :param self: this
        """
        self.exec(f"CALL aqi_clean({self._ceiling})")
