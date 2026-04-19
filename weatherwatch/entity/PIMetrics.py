from dataclasses import dataclass
from datetime import datetime

from entity.BaseEntity import BaseEntity
from sqlalchemy import Integer, Numeric
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ["PIMetrics"]


@dataclass
class PIMetrics(BaseEntity):
    """
    base sensor db enitity
    """

    __tablename__ = "pi_metrics"
    __table_args__ = {"extend_existing": True}

    read_time: Mapped[datetime] = mapped_column(DATETIME(fsp=6), nullable=False, default=None)
    cpu_temp_c: Mapped[float] = mapped_column(Numeric, nullable=False, default=None)

    mem_available: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    mem_used: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    mem_percent: Mapped[float] = mapped_column(Numeric, nullable=False, default=None)

    disk_available: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    disk_used: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    disk_percent: Mapped[float] = mapped_column(Numeric, nullable=False, default=None)

    cpu_temp_c: Mapped[float] = mapped_column(Numeric, nullable=False, default=None)
