from entity.IndoorSensor import IndoorSensor
from py_singleton import singleton
from repository.BaseRepository import BaseRepository

__all__ = ["IndoorSensorRepository"]


@singleton
class IndoorSensorRepository(BaseRepository[IndoorSensor]):

    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__(entity=IndoorSensor)
