from py_singleton import singleton

from entity.PIMetrics import PIMetrics
from repository.BaseRepository import BaseRepository

__all__ = ["PIMetricsRepository"]


@singleton
class PIMetricsRepository(BaseRepository[PIMetrics]):

    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__(entity=PIMetrics)
