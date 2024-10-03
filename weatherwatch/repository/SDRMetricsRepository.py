from entity.SDRMetricts import SDRMetrics
from py_singleton import singleton
from repository.BaseRepository import BaseRepository

__all__ = ["SDRMetricsRepository"]


@singleton
class SDRMetricsRepository(BaseRepository[SDRMetrics]):

    def __init__(self):
        """
        ctor
        :param self: this
        """
        super().__init__(entity=SDRMetrics)
