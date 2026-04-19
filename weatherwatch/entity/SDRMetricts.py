from dataclasses import dataclass
from datetime import datetime

from entity.BaseEntity import BaseEntity
from sqlalchemy import Integer
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ["SDRMetrics"]


@dataclass
class SDRMetrics(BaseEntity):
    """
    base sensor db enitity
    """

    __tablename__ = "sdr_metrics"
    __table_args__ = {"extend_existing": True}

    start_time: Mapped[datetime] = mapped_column(DATETIME(fsp=6), nullable=False, default=None)
    end_time: Mapped[datetime] = mapped_column(DATETIME(fsp=6), nullable=False, default=None)
    duration_sec: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    sensor_cnt: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
