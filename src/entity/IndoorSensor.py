from dataclasses import dataclass

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from entity.BaseSensor import BaseSensor

__all__ = ["IndoorSensor"]

@dataclass
class IndoorSensor(BaseSensor):
    __tablename__ = "indoor_sensor"
    __table_args__ = {"extend_existing": True}

    channel: Mapped[int] = mapped_column(Integer, nullable=False)
