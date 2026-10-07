from datetime import date, datetime
from typing import List, Union

from entity.IndoorSensor import IndoorSensor
from py_singleton import singleton
from repository.BaseRepository import BaseRepository
from repository.db_read import db_read
from sqlalchemy import and_
from sqlalchemy.orm import Session

__all__ = ["IndoorSensorRepository"]


@singleton
class IndoorSensorRepository(BaseRepository[IndoorSensor]):
    """
    indoor sensor repo
    """

    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__(entity=IndoorSensor)

    @db_read(default=None)
    def find_latest(self, c: int) -> IndoorSensor:
        """
        get the latest record
        :param self: this
        :param c: the cnannel id
        :return the latest record
        """
        session: Session = self._datastore.session
        try:
            return session.query(IndoorSensor).filter_by(channel=c).order_by(IndoorSensor.read_time.desc()).first()
        finally:
            session.close()

    # pylint: disable=duplicate-code
    @db_read(default=[])
    def find_greater_than_read_time(self, channel: int, dt: Union[date, datetime]) -> List[IndoorSensor]:
        """
        get records greater than the given date
        :param self: this
        :param channel: the channel id
        :param dt: the lower bound date (date or datetime; a bare date is treated as midnight)
        :return the list of records
        """
        session: Session = self._datastore.session
        try:
            return (
                session.query(IndoorSensor)
                .filter(and_(IndoorSensor.channel == channel, IndoorSensor.read_time > self._coerce_to_datetime(dt)))
                .order_by(IndoorSensor.read_time.desc())
                .all()
            )
        finally:
            session.close()
