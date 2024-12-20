from datetime import date, timedelta
from typing import Self

from dateutil.relativedelta import relativedelta
from util.Logger import logger

__all__ = ["BackupRange"]


@logger
class BackupRange:
    """
    backup date range data
    """

    def __init__(self, from_date: date, to_date: date, file_prefix: str):
        self._from_date = from_date
        self._to_date = to_date
        self._file_prefix = file_prefix

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

    @property
    def file_prefix(self) -> str:
        """
        _file_prefix string property getter
        :param self: this
        :return: the file_prefix
        """
        return self._file_prefix

    @staticmethod
    def prev_week() -> Self:
        """
        get and instance of the previous week
        :return: instance of the previous week
        """
        today: date = date.today()

        from_date: date = today - timedelta(days=today.weekday(), weeks=1)
        to_date: date = today - timedelta(days=today.weekday() + 1)

        return BackupRange(from_date, to_date, from_date.strftime("%Y-%m-%d"))

    @staticmethod
    def prev_month() -> Self:
        """
        https://stackoverflow.com/questions/66026812/find-start-and-end-date-of-previous-month-from-current-date-in-python
        get and instance of the previous month
        :return: instance of the previous month
        """
        today: date = date.today()

        from_date: date = today.replace(day=1) - relativedelta(months=1)
        to_date: date = from_date + relativedelta(months=1) - timedelta(days=1)

        return BackupRange(from_date, to_date, from_date.strftime("%Y-%m"))
