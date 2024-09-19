from src.entity import IndoorSensor
from src.repository import BaseRepository


class IndoorSensorRepository(BaseRepository[IndoorSensor]):
    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__()
