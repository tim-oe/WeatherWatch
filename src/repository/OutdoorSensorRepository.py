from src.entity.OutdoorSensor import OutdoorSensor
from src.repository.BaseRepository import BaseRepository

__all__ = ["OutdoorSensorRepository"]


class OutdoorSensorRepository(BaseRepository[OutdoorSensor]):
    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__(entity=OutdoorSensor)

    # override for singleton
    # https://www.geeksforgeeks.org/singleton-pattern-in-python-a-complete-guide/
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(OutdoorSensorRepository, cls).__new__(cls)
        return cls.instance
