from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from util.Logger import logger


@logger
class BaseEntity(DeclarativeBase):

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, default=None, autoincrement="auto")
