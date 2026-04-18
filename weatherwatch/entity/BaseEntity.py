from datetime import datetime

from sqlalchemy import DateTime, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from util.Logger import logger


@logger
class BaseEntity(DeclarativeBase):
    """
    base db enitity
    https://docs.sqlalchemy.org/en/20/tutorial/orm_related_objects.html
    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, default=None, autoincrement="auto")

    @classmethod
    def from_dict(cls, data: dict, **defaults):
        """
        create an entity instance from a dict, matching keys to mapped columns.
        defaults are used as fallbacks when a key is absent from data.
        string values for DateTime columns are auto-converted via fromisoformat.
        """
        mapper = inspect(cls).mapper
        col_attrs = {c.key: c.columns[0].type for c in mapper.column_attrs}

        kwargs = dict(defaults)
        for k, v in data.items():
            if k in col_attrs and k != "id":
                kwargs[k] = v

        for k in list(kwargs):
            if k in col_attrs and isinstance(col_attrs[k], DateTime) and isinstance(kwargs[k], str):
                kwargs[k] = datetime.fromisoformat(kwargs[k])

        return cls(**kwargs)
