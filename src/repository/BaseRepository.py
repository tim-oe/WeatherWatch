from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from src.repository import DataStore

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    DataStore for orm
    https://github.com/auth0-blog/sqlalchemy-orm-tutorial
    https://medium.com/@danielwume/must-know-package-to-build-your-system-real-world-examples-with-sqlalchemy-in-python-db8c72a0f6c1
    """

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._datastore: DataStore = DataStore()

    def insert(self, o: T):
        session: Session = self._datastore.session
        session.add(o)
        session.commit()

    def findById(self, id: int) -> T:
        session: Session = self._datastore.session
        return session.query(T).filter_by(id=id).first()

    # TODO this seems off but it's all the examples i found
    def update(self, o: T):
        session: Session = self._datastore.session
        session.commit()

    def delete(self, o: T):
        session: Session = self._datastore.session
        session.delete(o)
        session.commit()
