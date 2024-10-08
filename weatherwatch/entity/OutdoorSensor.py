from dataclasses import dataclass

from entity.BaseSensor import BaseSensor
from sqlalchemy import Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ["OutdoorSensor"]


@dataclass
class OutdoorSensor(BaseSensor):
    __tablename__ = "outdoor_sensor"
    __table_args__ = {"extend_existing": True}

    pressure: Mapped[float] = mapped_column(Numeric, nullable=False)

    rain_mm: Mapped[float] = mapped_column(Numeric, nullable=False)
    wind_avg_m_s: Mapped[float] = mapped_column(Numeric, nullable=False)
    wind_max_m_s: Mapped[float] = mapped_column(Numeric, nullable=False)
    wind_dir_deg: Mapped[int] = mapped_column(Integer, nullable=False)
    light_lux: Mapped[int] = mapped_column(Integer, nullable=False)
    uv: Mapped[float] = mapped_column(Numeric, nullable=False)
