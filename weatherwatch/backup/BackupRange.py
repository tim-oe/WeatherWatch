from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from util.Logger import logger
from typing import Self

__all__ = ["BackupRange"]


@logger
class BackupRange:
    """
    backup date range data
    """

    def __init__(self, from_date: date, to_date: date):
        self._from_date = from_date
        self._to_date = to_date

    @property
    def from_date(self) -> date:
        """
        from_date string property getter
        :param self: this
        :return: the from_date
        """
        return self._from_date

    @property
    def to_date(self) -> date:
        """
        to_date string property getter
        :param self: this
        :return: the to_date
        """
        return self._to_date

    @staticmethod
    def prev_week() -> Self:
        today: date = date.today()
        
        from_date: date = today - timedelta(days=today.weekday(), weeks=1)
        to_date: date = today - timedelta(days=today.weekday() + 1)

        return BackupRange(from_date, to_date)
        
    @staticmethod
    def prev_month() -> Self:
        """
        https://stackoverflow.com/questions/66026812/find-start-and-end-date-of-previous-month-from-current-date-in-python
        """
        today: date = date.today()
        
        from_date: date = today.replace(day=1) - relativedelta(months=1)
        to_date: date = from_date + relativedelta(months=1) - timedelta(days=1)

        return BackupRange(from_date, to_date)
