from datetime import date, datetime
from decimal import Decimal
from typing import List, Union

from entity.OutdoorSensor import OutdoorSensor
from py_singleton import singleton
from repository.BaseRepository import BaseRepository
from repository.db_read import db_read
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

    @db_read(default=None)
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
    @db_read(default=[])
    def find_greater_than_read_time(self, dt: Union[date, datetime]) -> List[OutdoorSensor]:
        """
        get records greater than the given date
        :param self: this
        :param dt: the lower bound date (date or datetime; a bare date is treated as midnight)
        :return the list of records
        """
        session: Session = self._datastore.session
        try:
            return (
                session.query(OutdoorSensor)
                .filter(OutdoorSensor.read_time > self._coerce_to_datetime(dt))
                .order_by(OutdoorSensor.read_time.desc())
                .all()
            )
        finally:
            session.close()

    @db_read(default=Decimal("0"))
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

    def after_drain(self, first_read_time):
        """
        recompute rain_delta_mm from the first replayed read_time onward
        :param self: this
        :param first_read_time: earliest replayed read_time
        """
        if first_read_time is None:
            return
        session: Session = self._datastore.session
        try:
            rows = (
                session.query(OutdoorSensor)
                .filter(OutdoorSensor.read_time >= first_read_time)
                .order_by(OutdoorSensor.sensor_id.asc(), OutdoorSensor.read_time.asc())
                .all()
            )
            previous_by_sensor = {}
            for row in rows:
                if row.sensor_id not in previous_by_sensor:
                    seed = (
                        session.query(OutdoorSensor)
                        .filter(
                            OutdoorSensor.sensor_id == row.sensor_id,
                            OutdoorSensor.read_time < first_read_time,
                        )
                        .order_by(OutdoorSensor.read_time.desc())
                        .first()
                    )
                    previous_by_sensor[row.sensor_id] = seed.rain_cum_mm if seed is not None else None
                previous = previous_by_sensor[row.sensor_id]
                if previous is None:
                    delta = Decimal("0")
                else:
                    delta = round(Decimal(str(row.rain_cum_mm)) - Decimal(str(previous)), 2)
                if delta < 0:
                    row.rain_delta_mm = round(Decimal(str(row.rain_cum_mm)), 2)
                else:
                    row.rain_delta_mm = delta
                previous_by_sensor[row.sensor_id] = row.rain_cum_mm
            session.commit()
        finally:
            session.close()
