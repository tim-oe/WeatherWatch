from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from util.Logger import logger


@logger
class BaseEntity(DeclarativeBase):
    """
    base db enitity
    https://docs.sqlalchemy.org/en/20/tutorial/orm_related_objects.html
    """

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, default=None, autoincrement="auto")
