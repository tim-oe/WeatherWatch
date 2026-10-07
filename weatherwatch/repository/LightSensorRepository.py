from datetime import date, datetime
from typing import List, Union

from entity.LightSensor import LightSensor
from py_singleton import singleton
from repository.BaseRepository import BaseRepository
from repository.db_read import db_read
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

    @db_read(default=None)
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

    # pylint: disable=duplicate-code
    @db_read(default=[])
    def find_greater_than_read_time(self, dt: Union[date, datetime]) -> List[LightSensor]:
        """
        get records greater than the given date
        :param self: this
        :param dt: the lower bound date (date or datetime; a bare date is treated as midnight)
        :return the list of records
        """
        session: Session = self._datastore.session
        try:
            return (
                session.query(LightSensor)
                .filter(LightSensor.read_time > self._coerce_to_datetime(dt))
                .order_by(LightSensor.read_time.desc())
                .all()
            )
        finally:
            session.close()
