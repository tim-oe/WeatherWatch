from datetime import datetime

from entity.BaseEntity import BaseEntity
from sqlalchemy import DateTime, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ["LightSensor"]


class LightSensor(BaseEntity):
    """
    light sensor db entity
    """

    __tablename__ = "light_sensor"
    __table_args__ = {"extend_existing": True}

    read_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=None)

    lux: Mapped[float] = mapped_column(Numeric, nullable=False, default=None)
    visible: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    infrared: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    full_spectrum: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    ir_visible_luminosity: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    ir_only: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
