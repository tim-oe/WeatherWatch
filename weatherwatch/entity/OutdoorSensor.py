from dataclasses import dataclass

from entity.BaseSensor import BaseSensor
from sqlalchemy import Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ["OutdoorSensor"]


@dataclass
class OutdoorSensor(BaseSensor):
    __tablename__ = "outdoor_sensor"
    __table_args__ = {"extend_existing": True}

    pressure: Mapped[float] = mapped_column(Numeric, nullable=False, default=None)

    rain_mm: Mapped[float] = mapped_column(Numeric, nullable=False, default=None)
    wind_avg_m_s: Mapped[float] = mapped_column(Numeric, nullable=False, default=None)
    wind_max_m_s: Mapped[float] = mapped_column(Numeric, nullable=False, default=None)
    wind_dir_deg: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    light_lux: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
    uv: Mapped[float] = mapped_column(Numeric, nullable=False, default=None)
