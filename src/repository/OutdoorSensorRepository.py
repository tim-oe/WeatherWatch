from src.entity.OutdoorSensor import OutdoorSensor
from src.repository.BaseRepository import BaseRepository

__all__ = ["OutdoorSensorRepository"]


class OutdoorSensorRepository(BaseRepository[OutdoorSensor]):
    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__()
