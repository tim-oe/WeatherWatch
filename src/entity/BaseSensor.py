from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Integer, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseSensor(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement="auto")
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    read_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    battery_ok: Mapped[bool] = mapped_column(Boolean, nullable=False)
    sensor_id: Mapped[int] = mapped_column(Integer, nullable=False)
    temperature_f: Mapped[float] = mapped_column(Numeric, nullable=False)
    humidity: Mapped[int] = mapped_column(Integer, nullable=False)
    mic: Mapped[str] = mapped_column(String(3), nullable=False)
    mod: Mapped[str] = mapped_column(String(3), nullable=False)
    freq: Mapped[float] = mapped_column(Numeric, nullable=False)
    snr: Mapped[float] = mapped_column(Numeric, nullable=False)
    noise: Mapped[float] = mapped_column(Numeric, nullable=False)
    raw: Mapped[str] = mapped_column(JSON, nullable=False)

    # override
    def __str__(self):
        return str(self.__dict__)

    # override
    def __repr__(self):
        return f"<{self.__name__} {self.__dict__}>"
