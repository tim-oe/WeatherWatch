from py_singleton import singleton

from entity.OutdoorSensor import OutdoorSensor
from repository.BaseRepository import BaseRepository

__all__ = ["OutdoorSensorRepository"]


@singleton
class OutdoorSensorRepository(BaseRepository[OutdoorSensor]):

    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__(entity=OutdoorSensor)
