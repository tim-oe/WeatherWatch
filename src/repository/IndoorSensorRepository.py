from src.entity.IndoorSensor import IndoorSensor
from src.repository.BaseRepository import BaseRepository

__all__ = ["IndoorSensorRepository"]


class IndoorSensorRepository(BaseRepository[IndoorSensor]):
    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__(entity=IndoorSensor)

    # override for singleton
    # https://www.geeksforgeeks.org/singleton-pattern-in-python-a-complete-guide/
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(IndoorSensorRepository, cls).__new__(cls)
        return cls.instance
