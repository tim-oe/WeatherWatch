from dataclasses import dataclass
from datetime import datetime

from entity.BaseEntity import BaseEntity
from sqlalchemy import DateTime, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ["PIMetrics"]


@dataclass
class PIMetrics(BaseEntity):
    __tablename__ = "pi_metrics"
    __table_args__ = {"extend_existing": True}

    read_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    cpu_temp_c: Mapped[float] = mapped_column(Numeric, nullable=False)

    mem_available: Mapped[int] = mapped_column(Integer, nullable=False)
    mem_used: Mapped[int] = mapped_column(Integer, nullable=False)
    mem_percent: Mapped[float] = mapped_column(Numeric, nullable=False)

    disk_available: Mapped[int] = mapped_column(Integer, nullable=False)
    disk_used: Mapped[int] = mapped_column(Integer, nullable=False)
    disk_percent: Mapped[float] = mapped_column(Numeric, nullable=False)

    cpu_temp_c: Mapped[float] = mapped_column(Numeric, nullable=False)
