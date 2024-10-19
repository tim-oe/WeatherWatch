from datetime import datetime

from entity.BaseEntity import BaseEntity
from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ["AQISensor"]


class AQISensor(BaseEntity):
    __tablename__ = "aqi_sensor"
    __table_args__ = {"extend_existing": True}

    read_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=None)

    pm_1_0_conctrt_std: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    pm_2_5_conctrt_std: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    pm_10_conctrt_std: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    pm_1_0_conctrt_atmosph: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    pm_2_5_conctrt_atmosph: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    pm_10_conctrt_atmosph: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
