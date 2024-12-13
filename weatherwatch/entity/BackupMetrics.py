from datetime import date, datetime

from entity.BaseEntity import BaseEntity
from sqlalchemy import Date, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ["BackupMetrics"]


class BackupMetrics(BaseEntity):
    __tablename__ = "backup_metrics"
    __table_args__ = {"extend_existing": True}

    to_date: Mapped[date] = mapped_column(Date, nullable=False, default=None)
    from_date: Mapped[date] = mapped_column(Date, nullable=False, default=None)
    table_name: Mapped[str] = mapped_column(String(64), nullable=False, default=None)
    backup_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=None)
