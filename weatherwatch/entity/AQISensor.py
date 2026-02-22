from datetime import datetime
from typing import Optional, Self

from entity.BaseEntity import BaseEntity
from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ["AQISensor"]

PM_FIELDS: list[str] = [
    "pm_1_0_conctrt_std",
    "pm_2_5_conctrt_std",
    "pm_10_conctrt_std",
    "pm_1_0_conctrt_atmosph",
    "pm_2_5_conctrt_atmosph",
    "pm_10_conctrt_atmosph",
]


class AQISensor(BaseEntity):
    """
    aqi sensor db enitity
    """

    __tablename__ = "aqi_sensor"
    __table_args__ = {"extend_existing": True}

    read_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=None)

    pm_1_0_conctrt_std: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    pm_2_5_conctrt_std: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    pm_10_conctrt_std: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    pm_1_0_conctrt_atmosph: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    pm_2_5_conctrt_atmosph: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    pm_10_conctrt_atmosph: Mapped[int] = mapped_column(Integer, nullable=False, default=None)

    def fudge(self, prev: Optional[Self], nxt: Optional[Self], ceiling: int):
        """
        replace outlying reads with the average of the nearest valid neighbors
        :param self: this
        :param prev: the nearest previous record not out of range
        :param nxt: the nearest next record not out of range
        :param ceiling: the max valid reading
        """
        for field in PM_FIELDS:
            if getattr(self, field) > ceiling:
                if prev is not None and nxt is not None:
                    setattr(self, field, (getattr(prev, field) + getattr(nxt, field)) // 2)
                elif prev is not None:
                    setattr(self, field, getattr(prev, field))
                elif nxt is not None:
                    setattr(self, field, getattr(nxt, field))
