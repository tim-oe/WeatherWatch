from entity.OutdoorSensor import OutdoorSensor
from repository.BaseRepository import BaseRepository
from util.Singleton import Singleton

__all__ = ["OutdoorSensorRepository"]


class OutdoorSensorRepository(Singleton, BaseRepository[OutdoorSensor]):

    def __init__(self):
        """
        ctor
        :param self: this
        """
        if self._initialized:
            return
        self._initialized = True

        super().__init__(entity=OutdoorSensor)
