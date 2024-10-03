from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseEntity(DeclarativeBase):

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, autoincrement="auto")

    # override
    def __str__(self):
        return str(self.__dict__)
