from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Integer, Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from util.Logger import logger

__all__ = ["BaseSensor"]


@logger
class BaseSensor(DeclarativeBase):
    """
    base sensor db enitity
    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, default=None, autoincrement="auto")
    read_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=None)
    battery_ok: Mapped[bool] = mapped_column(Boolean, nullable=False, default=None)
    sensor_id: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    temperature_f: Mapped[float] = mapped_column(Numeric, nullable=False, default=None)
    humidity: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    raw: Mapped[str] = mapped_column(JSON, nullable=False, default=None)
