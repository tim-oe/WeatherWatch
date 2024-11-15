from datetime import datetime
from typing import List

from entity.AQISensor import AQISensor
from py_singleton import singleton
from repository.BaseRepository import BaseRepository
from sqlalchemy import or_
from sqlalchemy.orm import Session

__all__ = ["AQISensorRepository"]


@singleton
class AQISensorRepository(BaseRepository[AQISensor]):

    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__(entity=AQISensor)

    def findLatest(self) -> AQISensor:
        session: Session = self._datastore.session
        try:
            return session.query(AQISensor).order_by(AQISensor.read_time.desc()).first()
        finally:
            session.close()

    def findGreaterThanReadTime(self, dt: datetime) -> List[AQISensor]:
        session: Session = self._datastore.session
        try:
            return session.query(AQISensor).filter(AQISensor.read_time > dt).order_by(AQISensor.read_time.desc()).all()
        finally:
            session.close()

    ##################################################################
    # below functions are for data cleaup with funky sensor readings
    # it's a lazy kludge
    ##################################################################
    def findPrevious(self, session: Session, id: int) -> AQISensor:
        return session.query(AQISensor).filter(AQISensor.id < id).order_by(AQISensor.id.desc()).first()

    def findNext(self, session: Session, id: int) -> AQISensor:
        return session.query(AQISensor).filter(AQISensor.id > id).order_by(AQISensor.id.asc()).first()

    def clean(self):
        session: Session = self._datastore.session
        try:
            for d in (
                session.query(AQISensor)
                .filter(
                    or_(
                        AQISensor.pm_1_0_conctrt_std > 1000,
                        AQISensor.pm_2_5_conctrt_std > 1000,
                        AQISensor.pm_10_conctrt_std > 1000,
                        AQISensor.pm_1_0_conctrt_atmosph > 1000,
                        AQISensor.pm_2_5_conctrt_atmosph > 1000,
                        AQISensor.pm_10_conctrt_atmosph > 1000,
                    )
                )
                .order_by(AQISensor.id.asc())
                .all()
            ):

                print(f"d {d.id}")
                p: AQISensor = self.findPrevious(session, d.id)
                if p is not None:
                    print(f"p {p.id}")
                    d.fudge(p)
                p2: AQISensor = self.findPrevious(session, p.id)
                if p2 is not None:
                    print(f"p2 {p2.id}")
                    d.fudge(p2)
                n: AQISensor = self.findNext(session, d.id)
                if n is not None:
                    print(f"n {p.id}")
                    d.fudge(n)
                n2: AQISensor = self.findNext(session, n.id)
                if n2 is not None:
                    print(f"n2 {n2.id}")
                    d.fudge(n2)

                session.commit()

        finally:
            session.close()
