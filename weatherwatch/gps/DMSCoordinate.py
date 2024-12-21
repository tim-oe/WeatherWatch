import math
from enum import Enum

from util.Logger import logger

__all__ = ["DMSCoordinate", "Ordinal"]


class Ordinal(Enum):
    """
    compass ordinal
    """

    NORTH = "N"
    SOUTH = "S"
    EAST = "E"
    WEST = "W"


@logger
class DMSCoordinate:
    """
    deg min sec geo coordinates
    https://stackoverflow.com/questions/2579535/convert-dd-decimal-degrees-to-dms-degrees-minutes-seconds-in-python
    """

    def __init__(self, dd=None, isLat: bool = True):
        neg = dd < 0
        dd = (-1) ** neg * dd
        dd, self._degrees = math.modf(dd)
        mins, self._minutes = math.modf(60 * dd)
        self._seconds = 60 * mins

        if isLat is True and neg is True:
            self._ordinal = Ordinal.SOUTH
        if isLat is True and neg is False:
            self._ordinal = Ordinal.NORTH
        if isLat is False and neg is True:
            self._ordinal = Ordinal.WEST
        if isLat is False and neg is False:
            self._ordinal = Ordinal.EAST

    @property
    def degrees(self):
        """
        degrees string property getter
        :param self: this
        :return: the degrees
        """
        return self._degrees

    @property
    def minutes(self):
        """
        minutes string property getter
        :param self: this
        :return: the minutes
        """
        return self._minutes

    @property
    def seconds(self):
        """
        seconds string property getter
        :param self: this
        :return: the seconds
        """
        return self._seconds

    @property
    def ordinal(self):
        """
        ordinal string property getter
        :param self: this
        :return: the ordinal
        """
        return self._ordinal
