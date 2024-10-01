from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from entity.BaseEntity import BaseEntity

__all__ = ["PIMetrics"]


class PIMetrics(BaseEntity):
    __tablename__ = "pi_metrics"
    __table_args__ = {"extend_existing": True}

    read_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    mem_info: Mapped[str] = mapped_column(String(128), nullable=False)
    disk_info: Mapped[str] = mapped_column(String(128), nullable=False)
    cpu_temp: Mapped[str] = mapped_column(String(16), nullable=False)
