from src.entity.IndoorSensor import IndoorSensor
from src.repository.BaseRepository import BaseRepository

__all__ = ["IndoorSensorRepository"]


class IndoorSensorRepository(BaseRepository[IndoorSensor]):
    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__()
