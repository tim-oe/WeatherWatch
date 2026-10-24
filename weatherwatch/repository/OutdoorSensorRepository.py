from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Union

from entity.OutdoorSensor import OutdoorSensor
from py_singleton import singleton
from repository.BaseRepository import BaseRepository
from repository.db_read import db_read
from sqlalchemy import func, text
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
        get the total rainfall for a UTC calendar day
        :param self: this
        :param rain_date: the UTC day to sum
        half-open range on read_time so outdoor_rain_day_idx can be used.
        bounds are UTC wall times and stay out of LocalToUTCDateTime.
        just after midnight the current day can still be empty
        """
        start = datetime(rain_date.year, rain_date.month, rain_date.day)
        end = start + timedelta(days=1)
        session: Session = self._datastore.session
        try:
            total = (
                session.query(func.sum(OutdoorSensor.rain_delta_mm))
                .filter(text("read_time >= :start AND read_time < :end"))
                .params(start=start, end=end)
                .scalar()
            )
            if total is None:
                return Decimal(0)

            return total
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
