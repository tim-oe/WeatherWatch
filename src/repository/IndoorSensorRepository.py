from entity.IndoorSensor import IndoorSensor
from repository.BaseRepository import BaseRepository
from util.Singleton import Singleton

__all__ = ["IndoorSensorRepository"]


class IndoorSensorRepository(Singleton, BaseRepository[IndoorSensor]):

    def __init__(self):
        """
        ctor
        :param self: this
        """
        if self._initialized:
            return
        self._initialized = True

        super().__init__(entity=IndoorSensor)
