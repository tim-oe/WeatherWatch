from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Integer, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

__all__ = ["BaseSensor"]


class BaseSensor(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, default=None, autoincrement="auto")
    read_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=None)
    battery_ok: Mapped[bool] = mapped_column(Boolean, nullable=False, default=None)
    sensor_id: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    temperature_f: Mapped[float] = mapped_column(Numeric, nullable=False, default=None)
    humidity: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    raw: Mapped[str] = mapped_column(JSON, nullable=False, default=None)
        
    # override
    def __str__(self):
        return f"<{self.__dict__}>"

   # override
    def __repr__(self):
        return self.__str__()
