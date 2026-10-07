import re
from datetime import datetime
from decimal import Decimal

from sqlalchemy import JSON, Boolean, DateTime, Integer, Numeric
from sqlalchemy.types import TypeDecorator

__all__ = ["EntityCodec"]

_OFFSET_RE = re.compile(r"T\d{2}:\d{2}:\d{2}(\.\d+)?-")


def _concrete_type(col_type):
    """
    unwrap TypeDecorator so LocalToUTCDateTime dispatches as DateTime
    :param col_type: the SQLAlchemy column type
    :return: the implementation type
    """
    current = col_type
    seen = set()
    while isinstance(current, TypeDecorator) and id(current) not in seen:
        seen.add(id(current))
        current = current.impl
    return current


def _encode_datetime(value: datetime) -> str:
    """
    naive isoformat, passed through unchanged
    :param value: the datetime value
    :return: the iso string
    """
    if value.tzinfo is not None:
        raise ValueError("datetime must be naive")
    return value.isoformat()


def _decode_datetime(value) -> datetime:
    """
    reject an offset-bearing string rather than stripping it
    :param value: the spooled string
    :return: a naive datetime
    """
    if not isinstance(value, str) or value.endswith("Z") or "+" in value or _OFFSET_RE.search(value):
        raise ValueError("offset-bearing datetime")
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is not None:
        raise ValueError("offset-bearing datetime")
    return parsed


def _encode_numeric(value):
    """
    :param value: the numeric value
    :return: a decimal string
    """
    return str(value)


def _encode_json(value):
    """
    :param value: the JSON value
    :return: the value unchanged
    """
    return value


def _decode_numeric(value):
    """
    :param value: the spooled numeric
    :return: a Decimal
    """
    return Decimal(str(value))


def _decode_bool(value):
    """
    :param value: the spooled boolean
    :return: the boolean
    """
    if not isinstance(value, bool):
        raise ValueError("boolean value must be bool")
    return value


def _decode_int(value):
    """
    :param value: the spooled integer
    :return: the integer
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("integer value must be int")
    return int(value)


_ENCODERS = (
    (DateTime, _encode_datetime),
    (Numeric, _encode_numeric),
    (Boolean, bool),
    (Integer, int),
    (JSON, _encode_json),
)

_DECODERS = (
    (DateTime, _decode_datetime),
    (Numeric, _decode_numeric),
    (Boolean, _decode_bool),
    (Integer, _decode_int),
    (JSON, _encode_json),
)


def _dispatch(table, col_type, value):
    """
    apply the first matching column-type handler
    :param table: encoder or decoder pairs
    :param col_type: the SQLAlchemy column type
    :param value: the column value
    :return: the converted value
    """
    concrete = _concrete_type(col_type)
    for type_cls, handler in table:
        if isinstance(concrete, type_cls):
            return handler(value)
    return value


def encode_value(col_type, value):
    """
    encode one column value by column type
    :param col_type: the SQLAlchemy column type
    :param value: the attribute value
    :return: a JSON-safe value
    """
    if value is None:
        return None
    return _dispatch(_ENCODERS, col_type, value)


def decode_value(col_type, value):
    """
    decode one column value by column type
    :param col_type: the SQLAlchemy column type
    :param value: the JSON value
    :return: the attribute value
    """
    if value is None:
        return None
    return _dispatch(_DECODERS, col_type, value)


class EntityCodec:
    """
    serialize entities from the SQLAlchemy mapper
    """

    @staticmethod
    def encode(entity) -> dict:
        """
        encode mapper columns except id
        :param entity: the entity instance
        :return: column name to JSON value
        """
        data = {}
        for column in type(entity).__table__.columns:
            if column.name == "id":
                continue
            data[column.name] = encode_value(column.type, getattr(entity, column.name))
        return data

    @staticmethod
    def decode(entity_cls, data: dict):
        """
        build an entity from spooled column data
        :param entity_cls: the entity class
        :param data: the envelope data object
        :return: the entity instance
        """
        entity = entity_cls()
        for column in entity_cls.__table__.columns:
            if column.name == "id" or column.name not in data:
                continue
            setattr(entity, column.name, decode_value(column.type, data[column.name]))
        return entity
