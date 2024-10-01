from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from entity.BaseEntity import BaseEntity

__all__ = ["SDRMetrics"]


@dataclass
class SDRMetrics(BaseEntity):
    __tablename__ = "sdr_metrics"
    __table_args__ = {"extend_existing": True}

    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration_sec: Mapped[int] = mapped_column(Integer, nullable=False)
    sensor_cnt: Mapped[int] = mapped_column(Integer, nullable=False)
