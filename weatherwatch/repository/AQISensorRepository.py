from datetime import date, datetime
from typing import List

from entity.AQISensor import AQISensor
from py_singleton import singleton
from repository.BaseRepository import BaseRepository
from sqlalchemy import DATE, cast, or_
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

    def find_latest(self) -> AQISensor:
        """
        get the latest record
        :param self: this
        :return the latest record
        """
        session: Session = self._datastore.session
        try:
            return session.query(AQISensor).order_by(AQISensor.read_time.desc()).first()
        finally:
            session.close()

    def find_greater_than_read_time(self, dt: datetime) -> List[AQISensor]:
        """
        get records greater than the given date
        :param self: this
        :param dt: the lower bound date
        :return the list of records
        """
        session: Session = self._datastore.session
        try:
            return session.query(AQISensor).filter(AQISensor.read_time > dt).order_by(AQISensor.read_time.desc()).all()
        finally:
            session.close()

    def backup(self, from_date: date, to_date: date, file_name: str):
        """
        generate backup file for a given data range
        :param self: this
        :param from_date: from date
        :param to_date: to date
        :param file_name: the backup file name
        """
        with open(file_name, "w", encoding="utf-8") as f:
            session: Session = self._datastore.session
            try:
                for v in session.query(AQISensor).filter(cast(AQISensor.read_time, DATE).between(from_date, to_date)):
                    f.write(f"{self.get_insert(v)};\n")
            finally:
                f.close()
                session.close()

    ##################################################################
    # below functions are for data cleaup with funky sensor readings
    # it's a lazy kludge
    ##################################################################
    def find_previous(self, session: Session, id: int) -> AQISensor:
        """
        find previous record based on id
        :param self: this
        :param session: session the db session
        :param id: the current record id
        :return the previous record
        """
        return session.query(AQISensor).filter(AQISensor.id < id).order_by(AQISensor.id.desc()).first()

    def find_next(self, session: Session, id: int) -> AQISensor:
        """
        find next record based on id
        :param self: this
        :param session: session the db session
        :param id: the current record id
        :return the next record
        """
        return session.query(AQISensor).filter(AQISensor.id > id).order_by(AQISensor.id.asc()).first()

    def clean(self):
        """
        clean records of date outside of data range
        :param self: this
        """
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
                p: AQISensor = self.find_previous(session, d.id)
                if p is not None:
                    print(f"p {p.id}")
                    d.fudge(p)
                p2: AQISensor = self.find_previous(session, p.id)
                if p2 is not None:
                    print(f"p2 {p2.id}")
                    d.fudge(p2)
                n: AQISensor = self.find_next(session, d.id)
                if n is not None:
                    print(f"n {p.id}")
                    d.fudge(n)
                n2: AQISensor = self.find_next(session, n.id)
                if n2 is not None:
                    print(f"n2 {n2.id}")
                    d.fudge(n2)

                session.commit()

        finally:
            session.close()
