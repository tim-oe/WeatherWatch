from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.entity import BaseSensor


class IndoorSensor(BaseSensor):
    __tablename__ = "indoor_sensor"
    channel: Mapped[int] = mapped_column(Integer, nullable=False)
