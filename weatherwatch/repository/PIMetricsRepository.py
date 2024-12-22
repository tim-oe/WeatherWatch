from entity.PIMetrics import PIMetrics
from py_singleton import singleton
from repository.BaseRepository import BaseRepository

__all__ = ["PIMetricsRepository"]


@singleton
class PIMetricsRepository(BaseRepository[PIMetrics]):
    """
    pi metrics sensor repo
    """

    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__(entity=PIMetrics)
