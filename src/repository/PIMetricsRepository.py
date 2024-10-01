from py_singleton import singleton

from repository.BaseRepository import BaseRepository
from entity.PiMetrics import PIMetrics

__all__ = ["PiMetricsRepository"]


@singleton
class PIMetricsRepository(BaseRepository[PIMetrics]):

    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__(entity=PIMetrics)
