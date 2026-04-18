from datetime import datetime
from typing import Optional

from entity.BaseEntity import BaseEntity
from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ["TemperatureReading"]


class TemperatureReading(BaseEntity):
    """
    temperature sensor reading db entity
    """

    __tablename__ = "temperature_readings"
    __table_args__ = {"extend_existing": True}

    type: Mapped[str] = mapped_column(String(32), nullable=False, default="temperature")
    name: Mapped[str] = mapped_column(String(64), nullable=False, default=None)
    read_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=None)
    read_duration_ms: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True, default=None)

    value: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False, default=None)
    unit: Mapped[str] = mapped_column(String(4), nullable=False, default="C")
