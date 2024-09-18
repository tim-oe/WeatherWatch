from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy import Integer

from src.entity import BaseSensor

class IndoorSensor(BaseSensor):
    __tablename__ = 'indoor_sensor'   
    channel: Mapped[int] = mapped_column(Integer, nullable=False)
