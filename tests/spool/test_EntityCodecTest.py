import unittest
from datetime import datetime
from decimal import Decimal

from sqlalchemy import JSON, Boolean, DateTime, Integer, Numeric
from sqlalchemy.types import TypeDecorator

from entity.AQISensor import AQISensor
from entity.IndoorSensor import IndoorSensor
from entity.LightSensor import LightSensor
from entity.OutdoorSensor import OutdoorSensor
from entity.PIMetrics import PIMetrics
from entity.SDRMetricts import SDRMetrics
from spool.EntityCodec import EntityCodec, decode_value


def _concrete(col_type):
    current = col_type
    while isinstance(current, TypeDecorator):
        current = current.impl
    return current


def _fill(entity):
    for column in type(entity).__table__.columns:
        if column.name == "id":
            continue
        concrete = _concrete(column.type)
        if isinstance(concrete, DateTime):
            setattr(entity, column.name, datetime(2026, 3, 4, 5, 6, 7))
        elif isinstance(concrete, Numeric):
            setattr(entity, column.name, 1.25)
        elif isinstance(concrete, Boolean):
            setattr(entity, column.name, False)
        elif isinstance(concrete, Integer):
            setattr(entity, column.name, 7)
        elif isinstance(concrete, JSON):
            setattr(entity, column.name, {"time": "2026-03-04 05:06:07", "rain_mm": 1.25})


class EntityCodecTest(unittest.TestCase):

    def test_all_entities_round_trip_mapper_columns(self):
        for cls in (OutdoorSensor, IndoorSensor, AQISensor, LightSensor, PIMetrics, SDRMetrics):
            original = cls()
            _fill(original)
            encoded = EntityCodec.encode(original)
            self.assertNotIn("id", encoded)
            for column in cls.__table__.columns:
                if column.name != "id":
                    self.assertIn(column.name, encoded)
            restored = EntityCodec.decode(cls, encoded)
            for column in cls.__table__.columns:
                if column.name == "id":
                    continue
                actual = getattr(restored, column.name)
                expected = getattr(original, column.name)
                concrete = _concrete(column.type)
                if isinstance(concrete, Numeric):
                    self.assertEqual(Decimal(str(expected)), actual)
                else:
                    self.assertEqual(expected, actual)

    def test_numeric_float_is_encoded_as_string(self):
        entity = OutdoorSensor()
        _fill(entity)
        entity.rain_cum_mm = 3.5
        encoded = EntityCodec.encode(entity)
        self.assertEqual("3.5", encoded["rain_cum_mm"])
        self.assertIsInstance(encoded["rain_cum_mm"], str)

    def test_datetime_rejects_offset(self):
        column = OutdoorSensor.__table__.columns.read_time
        with self.assertRaises(ValueError):
            decode_value(column.type, "2026-03-04T05:06:07+00:00")
        with self.assertRaises(ValueError):
            decode_value(column.type, "2026-03-04T05:06:07-05:00")
