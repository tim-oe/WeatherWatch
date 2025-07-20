from typing import Self

from util.Logger import logger

__all__ = ["Hm3301Data"]


@logger
class Hm3301Data:
    """
    aqi sensor data
    """

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self.pm_1_0_conctrt_std = 0
        self.pm_2_5_conctrt_std = 0
        self.pm_10_conctrt_std = 0

        self.pm_1_0_conctrt_atmosph = 0
        self.pm_2_5_conctrt_atmosph = 0
        self.pm_10_conctrt_atmosph = 0

    def high(self, ceiling: int) -> bool:
        """
        test if data has out of range value
        :param self: this
        """
        is_high: bool = False

        if self.pm_1_0_conctrt_std > ceiling:
            is_high = True
        if self.pm_2_5_conctrt_std > ceiling:
            is_high = True
        if self.pm_10_conctrt_std > ceiling:
            is_high = True
        if self.pm_1_0_conctrt_atmosph > ceiling:
            is_high = True
        if self.pm_2_5_conctrt_atmosph > ceiling:
            is_high = True
        if self.pm_10_conctrt_atmosph > ceiling:
            is_high = True
        return is_high

    def lower(self, that: Self):
        """
        set values to the lower value
        :param self: this
        :param that: the object to level set with
        """
        self.pm_1_0_conctrt_std = min(self.pm_1_0_conctrt_std, that.pm_1_0_conctrt_std)
        self.pm_2_5_conctrt_std = min(self.pm_2_5_conctrt_std, that.pm_2_5_conctrt_std)
        self.pm_10_conctrt_std = min(self.pm_10_conctrt_std, that.pm_10_conctrt_std)
        self.pm_1_0_conctrt_atmosph = min(self.pm_1_0_conctrt_atmosph, that.pm_1_0_conctrt_atmosph)
        self.pm_2_5_conctrt_atmosph = min(self.pm_2_5_conctrt_atmosph, that.pm_2_5_conctrt_atmosph)
        self.pm_10_conctrt_atmosph = min(self.pm_10_conctrt_atmosph, that.pm_10_conctrt_atmosph)

    @property
    def pm_1_0_conctrt_std(self) -> int:
        """
        pm_1_0_conctrt_std property getter
        PM1.0 Standard particulate matter concentration Unit:ug/m3
        :param self: this
        :return: the pm_1_0_conctrt_std
        """
        return self._pm_1_0_conctrt_std

    @pm_1_0_conctrt_std.setter
    def pm_1_0_conctrt_std(self, pm_1_0_conctrt_std: int):
        """
        pm_1_0_conctrt_std property setter
        PM1.0 Standard particulate matter concentration Unit:ug/m3
        :param self: this
        :param: the pm_1_0_conctrt_std
        """
        self._pm_1_0_conctrt_std = pm_1_0_conctrt_std

    @property
    def pm_2_5_conctrt_std(self) -> int:
        """
        pm_2_5_conctrt_std property getter
        PM2.5 Standard particulate matter concentration Unit:ug/m3
        :param self: this
        :return: the pm_2_5_conctrt_std
        """
        return self._pm_2_5_conctrt_std

    @pm_2_5_conctrt_std.setter
    def pm_2_5_conctrt_std(self, pm_2_5_conctrt_std: int):
        """
        pm_2_5_conctrt_std property setter
        PM2.5 Standard particulate matter concentration Unit:ug/m3
        :param self: this
        :param: the pm_2_5_conctrt_std
        """
        self._pm_2_5_conctrt_std = pm_2_5_conctrt_std

    @property
    def pm_10_conctrt_std(self) -> int:
        """
        pm_10_conctrt_std property getter
        PM10 Standard particulate matter concentration Unit:ug/m3
        :param self: this
        :return: the pm_10_conctrt_std
        """
        return self._pm_10_conctrt_std

    @pm_10_conctrt_std.setter
    def pm_10_conctrt_std(self, pm_10_conctrt_std: int):
        """
        pm_10_conctrt_std property setter
        PM10  Standard particulate matter concentration Unit:ug/m3
        :param self: this
        :param: the pm_10_conctrt_std
        """
        self._pm_10_conctrt_std = pm_10_conctrt_std

    @property
    def pm_1_0_conctrt_atmosph(self) -> int:
        """
        pm_1_0_conctrt_atmosph property getter
        PM1.0 Atmospheric environment concentration ,unit:ug/m3
        :param self: this
        :return: the pm_1_0_conctrt_atmosph
        """
        return self._pm_1_0_conctrt_atmosph

    @pm_1_0_conctrt_atmosph.setter
    def pm_1_0_conctrt_atmosph(self, pm_1_0_conctrt_atmosph: int):
        """
        pm_1_0_conctrt_atmosph property setter
        PM1.0 Atmospheric environment concentration ,unit:ug/m3
        :param self: this
        :param: the pm_1_0_conctrt_atmosph
        """
        self._pm_1_0_conctrt_atmosph = pm_1_0_conctrt_atmosph

    @property
    def pm_2_5_conctrt_atmosph(self) -> int:
        """
        pm_2_5_conctrt_atmosph property getter
        PM2.5 Atmospheric environment concentration ,unit:ug/m3
        :param self: this
        :return: the pm_2_5_conctrt_atmosph
        """
        return self._pm_2_5_conctrt_atmosph

    @pm_2_5_conctrt_atmosph.setter
    def pm_2_5_conctrt_atmosph(self, pm_2_5_conctrt_atmosph: int):
        """
        pm_2_5_conctrt_atmosph property setter
        PM2.5 Atmospheric environment concentration ,unit:ug/m3
        :param self: this
        :param: the pm_2_5_conctrt_atmosph
        """
        self._pm_2_5_conctrt_atmosph = pm_2_5_conctrt_atmosph

    @property
    def pm_10_conctrt_atmosph(self) -> int:
        """
        pm_10_conctrt_atmosph property getter
        PM10  Atmospheric environment concentration ,unit:ug/m3
        :param self: this
        :return: the pm_10_conctrt_atmosph
        """
        return self._pm_10_conctrt_atmosph

    @pm_10_conctrt_atmosph.setter
    def pm_10_conctrt_atmosph(self, pm_10_conctrt_atmosph: int):
        """
        pm_10_conctrt_atmosph property setter
        PM10  Atmospheric environment concentration ,unit:ug/m3
        :param self: this
        :param: the pm_10_conctrt_atmosph
        """
        self._pm_10_conctrt_atmosph = pm_10_conctrt_atmosph
