from datetime import datetime, tzinfo
from decimal import Decimal

import axiompy
import pytz
import tzlocal
from axiompy import Units

__all__ = ["Converter"]


class Converter:
    MPS_TO_MPH_FACTOR: Decimal = Decimal("2.23694")
    HPA_TO_IOM_FACTOR: Decimal = Decimal("0.02953")
    LUX_TO_WPM_FACTOR: Decimal = Decimal("0.0079")

    UNITS = Units()

    @staticmethod
    def mm_to_inch(mm: float) -> float:
        """
        https://github.com/ArztKlein/Axiompy
        """
        units = Converter.UNITS
        ret: axiompy.value.Value = units.unit_convert(mm * units.millimetre, units.inch)
        return ret.value

    @staticmethod
    def mps_to_mph(mph: Decimal) -> Decimal:
        """
        https://www.quora.com/How-do-I-convert-m-s-to-mph
        """
        return mph * Converter.MPS_TO_MPH_FACTOR

    @staticmethod
    def hpa_to_iom(hpa: Decimal) -> Decimal:
        """
        https://www.xconvert.com/unit-converter/hectopascals-to-inches-of-mercury
        """
        return hpa * Converter.HPA_TO_IOM_FACTOR

    @staticmethod
    def lux_to_wpm(lux: Decimal) -> Decimal:
        """
        https://www.researchgate.net/post/Howto_convert_solar_intensity_in_LUX_to_watt_per_meter_square_for_sunlight
        """
        return lux * Converter.LUX_TO_WPM_FACTOR

    @staticmethod
    def to_utc(readTime: datetime, tz: str = tzlocal.get_localzone_name()) -> datetime:
        """
        https://www.researchgate.net/post/Howto_convert_solar_intensity_in_LUX_to_watt_per_meter_square_for_sunlight
        """
        tzlocal
        local_tz: tzinfo = pytz.timezone(tz)
        local_dt: datetime = local_tz.localize(readTime, is_dst=None)
        return local_dt.astimezone(pytz.utc)

    @staticmethod
    def tzname_to_fullname(tzname):
        """
        param: txname 3 letter tz code
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
