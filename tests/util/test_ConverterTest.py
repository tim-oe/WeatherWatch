from datetime import datetime
from decimal import Decimal
import unittest

from tzlocal import get_localzone_name

from util.Converter import Converter

class ConverterTest(unittest.TestCase):
    def test(self):        
        self.assertEqual(Converter.MPS_TO_MPH_FACTOR, Converter.mps_to_mph(Decimal(1.0)))
        self.assertEqual(Converter.HPA_TO_IOM_FACTOR, Converter.hpa_to_iom(Decimal(1.0)))
        self.assertEqual(Converter.LUX_TO_WPM_FACTOR, Converter.lux_to_wpm(Decimal(1.0)))
        self.assertEqual(Decimal(1.0), Decimal(round(Converter.mm_to_inch(float(Decimal(25.4))),2)))

        print(f"system timezone [{Converter.tzname_to_fullname(datetime.now().astimezone().tzinfo.tzname(None))}]")

        curr: datetime = datetime.now()
        print(curr)
        then: datetime = Converter.to_utc(curr)
        print(then)
        
        dif = int((then.replace(tzinfo=None) - curr).total_seconds() / (60 * 60))
        
        self.assertTrue(dif == 6 or dif == 5)
        
        print()
        
