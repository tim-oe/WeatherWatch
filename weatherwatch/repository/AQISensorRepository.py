from entity.AQISensor import AQISensor
from py_singleton import singleton
from repository.BaseRepository import BaseRepository

__all__ = ["AQISensorRepository"]


@singleton
class AQISensorRepository(BaseRepository[AQISensor]):

    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__(entity=AQISensor)
