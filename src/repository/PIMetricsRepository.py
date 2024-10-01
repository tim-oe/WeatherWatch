from py_singleton import singleton

from repository.BaseRepository import BaseRepository
from entity.PIMetrics import PIMetrics

__all__ = ["PIMetricsRepository"]


@singleton
class PIMetricsRepository(BaseRepository[PIMetrics]):

    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__(entity=PIMetrics)
