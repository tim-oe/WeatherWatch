from dataclasses import dataclass

from entity.BaseSensor import BaseSensor
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ["IndoorSensor"]


@dataclass
class IndoorSensor(BaseSensor):
    __tablename__ = "indoor_sensor"
    __table_args__ = {"extend_existing": True}

    channel: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
