from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseEntity(DeclarativeBase):

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False, default=None, autoincrement="auto")

    # override
    def __str__(self):
        return f"<{self.__dict__}>"

   # override
    def __repr__(self):
        return self.__str__()
