from entity.OutdoorSensor import OutdoorSensor
from py_singleton import singleton
from repository.BaseRepository import BaseRepository
from sqlalchemy.orm import Session

__all__ = ["OutdoorSensorRepository"]


@singleton
class OutdoorSensorRepository(BaseRepository[OutdoorSensor]):

    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__(entity=OutdoorSensor)

    def findLatest(self) -> OutdoorSensor:
        session: Session = self._datastore.session
        try:
            return session.query(OutdoorSensor).order_by(OutdoorSensor.read_time.desc()).first()
        finally:
            session.close()
