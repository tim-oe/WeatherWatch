from entity.IndoorSensor import IndoorSensor
from py_singleton import singleton
from repository.BaseRepository import BaseRepository
from sqlalchemy.orm import Session

__all__ = ["IndoorSensorRepository"]


@singleton
class IndoorSensorRepository(BaseRepository[IndoorSensor]):

    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__(entity=IndoorSensor)

    def findLatest(self, channel: int) -> IndoorSensor:
        session: Session = self._datastore.session
        try:
            return session.query(IndoorSensor).filter_by(channel=channel).order_by(IndoorSensor.read_time.desc()).first()
        finally:
            session.close()
