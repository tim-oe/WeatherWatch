from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy import String
from sqlalchemy import Numeric
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import DateTime
from sqlalchemy import Boolean

from datetime import datetime

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

    #override
    def __str__(self):
        return str(self.__dict__)
    
    #override
    def __repr__(self):
        return f"<{self.__name__} {self.__dict__}>"