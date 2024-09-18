from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy import Integer
from sqlalchemy import Numeric

from src.entity import BaseSensor

class OutdoorSensor(BaseSensor):
    __tablename__ = 'outdoor_sensor'   
    rain_mm: Mapped[float] = mapped_column(Numeric, nullable=False)
    wind_avg_m_s: Mapped[float] = mapped_column(Numeric, nullable=False)
    wind_max_m_s: Mapped[float] = mapped_column(Numeric, nullable=False)
    wind_dir_deg: Mapped[int] = mapped_column(Integer, nullable=False)
    light_lux: Mapped[int] = mapped_column(Integer, nullable=False)
    uv: Mapped[float] = mapped_column(Numeric, nullable=False)