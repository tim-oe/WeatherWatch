from entity.BackupMetrics import BackupMetrics
from py_singleton import singleton
from repository.BaseRepository import BaseRepository
from sqlalchemy.orm import Session

__all__ = ["BackupMetricsRepository"]


@singleton
class BackupMetricsRepository(BaseRepository[BackupMetrics]):

    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__(entity=BackupMetrics)

    def findLatest(self, table: str) -> BackupMetrics:
        session: Session = self._datastore.session
        try:
            return session.query(BackupMetrics).filter_by(table_name=table).order_by(BackupMetrics.backup_time.desc()).first()
        finally:
            session.close()
