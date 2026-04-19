from dataclasses import dataclass
from datetime import datetime

from entity.BaseSensor import BaseSensor
from sqlalchemy import Integer
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ["IndoorSensor"]


@dataclass
class IndoorSensor(BaseSensor):
    """
    indoor sensor db enitity
    """

    __tablename__ = "indoor_sensor"
    __table_args__ = {"extend_existing": True}

    read_time: Mapped[datetime] = mapped_column(DATETIME(fsp=6), nullable=False, default=None)

    channel: Mapped[int] = mapped_column(Integer, nullable=False, default=None)
