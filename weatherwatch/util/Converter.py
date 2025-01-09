from datetime import datetime, tzinfo
from decimal import Decimal

import axiompy
import pytz
import tzlocal
from axiompy import Units

__all__ = ["Converter"]


class Converter:
    """
    conversion utilies
    """

    MPS_TO_MPH_FACTOR: Decimal = Decimal("2.23694")
    HPA_TO_IOM_FACTOR: Decimal = Decimal("0.02953")
    LUX_TO_WPM_FACTOR: Decimal = Decimal("0.0079")

    UNITS = Units()

    @staticmethod
    def f_to_c(f: float) -> float:
        """
        convert fahrenheit to celsius
        :param f: fahrenheit to convert
        :return: celsius
        """
        return (f - 32) * 5 / 9

    @staticmethod
    def c_to_f(c: float) -> float:
        """
        convert celsius to fahrenheit
        :param c: celsius to convert
        :return: fahrenheit
        """
        return (c * 9 / 5) + 32

    @staticmethod
    def mm_to_inch(mm: float) -> float:
        """
        convert milimeters to inches
        :param mm: milimeters to convert
        :return: inches
        https://github.com/ArztKlein/Axiompy
        """
        units = Converter.UNITS
        ret: axiompy.value.Value = units.unit_convert(mm * units.millimetre, units.inch)
        return ret.value

    @staticmethod
    def mps_to_mph(mps: Decimal) -> Decimal:
        """
        convert miles/second to miles/hr
        :param mps: miles/second to convert
        :return: miles per hour
        https://www.quora.com/How-do-I-convert-m-s-to-mph
        """
        return mps * Converter.MPS_TO_MPH_FACTOR

    @staticmethod
    def hpa_to_iom(hpa: Decimal) -> Decimal:
        """
        convert hectopascal to inches of mercury
        :param hpa: hectopascal to convert
        :return: inches of mercury
        https://www.xconvert.com/unit-converter/hectopascals-to-inches-of-mercury
        """
        return hpa * Converter.HPA_TO_IOM_FACTOR

    @staticmethod
    def lux_to_wpm(lux: Decimal) -> Decimal:
        """
        convert lux to watt per meter square
        :param lux: lux to convert
        :return: watt per meter square
        https://www.researchgate.net/post/Howto_convert_solar_intensity_in_LUX_to_watt_per_meter_square_for_sunlight
        """
        return lux * Converter.LUX_TO_WPM_FACTOR

    @staticmethod
    def to_utc(read_time: datetime, tz: str = tzlocal.get_localzone_name()) -> datetime:
        """
        convert local time to UTC
        :param read_time: the time to convert
        :param tz: time timezone
        :return: time in UTC
        https://www.researchgate.net/post/Howto_convert_solar_intensity_in_LUX_to_watt_per_meter_square_for_sunlight
        """
        local_tz: tzinfo = pytz.timezone(tz)
        local_dt: datetime = local_tz.localize(read_time, is_dst=None)
        return local_dt.astimezone(pytz.utc)

    @staticmethod
    def tzname_to_fullname(tzname) -> str:
        """
        param: tzname 3 letter tz code
        :return: the timezone full name
        WTF does the default return a value that can't be used to set it...
        https://stackoverflow.com/questions/3489183/how-can-i-get-a-human-readable-timezone-name-in-python
        """
        # initial pass try for us...
        for timezone in pytz.all_timezones:
            if datetime.now(pytz.timezone(timezone)).tzname() == tzname and timezone.startswith("US/"):
                return timezone

        for timezone in pytz.all_timezones:
            if datetime.now(pytz.timezone(timezone)).tzname():
                return timezone

        raise ValueError(f"unkown tz {tzname}")

    @staticmethod
    def duration_seconds(start: datetime) -> int:
        """
        calculate the execution duration from start to now
        :param start: the processing start time
        :return duration in seconds
        """
        current = datetime.now()
        return int((current - start).total_seconds())
