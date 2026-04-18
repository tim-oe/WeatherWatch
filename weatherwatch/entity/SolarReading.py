from datetime import datetime
from typing import Optional

from entity.BaseEntity import BaseEntity
from sqlalchemy import DateTime, Integer, Numeric, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

__all__ = ["SolarReading"]


class SolarReading(BaseEntity):
    """
    solar charge controller reading db entity
    """

    __tablename__ = "solar_readings"
    __table_args__ = {"extend_existing": True}

    type: Mapped[str] = mapped_column(String(32), nullable=False, default="solar")
    name: Mapped[str] = mapped_column(String(64), nullable=False, default=None)
    read_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=None)
    read_duration_ms: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True, default=None)

    model: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, default=None)
    device_id: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True, default=None)

    battery_percentage: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True, default=None)
    battery_voltage: Mapped[Optional[float]] = mapped_column(Numeric(6, 1), nullable=True, default=None)
    battery_current: Mapped[Optional[float]] = mapped_column(Numeric(7, 2), nullable=True, default=None)
    battery_temperature: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True, default=None)
    battery_type: Mapped[Optional[str]] = mapped_column(String(16), nullable=True, default=None)

    controller_temperature: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True, default=None)
    charging_status: Mapped[Optional[str]] = mapped_column(String(24), nullable=True, default=None)

    load_status: Mapped[Optional[str]] = mapped_column(String(8), nullable=True, default=None)
    load_voltage: Mapped[Optional[float]] = mapped_column(Numeric(6, 1), nullable=True, default=None)
    load_current: Mapped[Optional[float]] = mapped_column(Numeric(7, 2), nullable=True, default=None)
    load_power: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True, default=None)

    pv_voltage: Mapped[Optional[float]] = mapped_column(Numeric(6, 1), nullable=True, default=None)
    pv_current: Mapped[Optional[float]] = mapped_column(Numeric(7, 2), nullable=True, default=None)
    pv_power: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True, default=None)

    battery_min_voltage_today: Mapped[Optional[float]] = mapped_column(Numeric(6, 1), nullable=True, default=None)
    battery_max_voltage_today: Mapped[Optional[float]] = mapped_column(Numeric(6, 1), nullable=True, default=None)
    max_charging_current_today: Mapped[Optional[float]] = mapped_column(Numeric(7, 2), nullable=True, default=None)
    max_discharging_current_today: Mapped[Optional[float]] = mapped_column(Numeric(7, 2), nullable=True, default=None)
    max_charging_power_today: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True, default=None)
    max_discharging_power_today: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True, default=None)
    charging_amp_hours_today: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True, default=None)
    discharging_amp_hours_today: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True, default=None)
    power_generation_today: Mapped[Optional[float]] = mapped_column(Numeric(10, 1), nullable=True, default=None)
    power_consumption_today: Mapped[Optional[float]] = mapped_column(Numeric(10, 1), nullable=True, default=None)

    power_generation_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=None)
