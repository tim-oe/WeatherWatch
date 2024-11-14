from datetime import datetime
from decimal import Decimal
import unittest
from urllib.parse import urlparse

from util.Converter import Converter
from wu.WUClient import WUClient
from wu.WUData import WUData

class WUClientTest(unittest.TestCase):

    def test(self): 
        client: WUClient = WUClient()        

        data: WUData = WUData(
                 winddir=180, 
                 windspeedmph=Decimal('1.2'), 
                 windgustmph=Decimal('2.3'),
                 humidity=55,
                 tempf=Decimal('70.72'),
                 dailyrainin=Decimal('0.3'),
                 baromin=Decimal('29.89'),
                 solarradiation=Decimal('1.2'),
                 uv=Decimal('1.1'),
                 indoortempf=Decimal('68.3'),
                 indoorhumidity=40)

        client.post(datetime.now(), data, endPoint=urlparse("http://www.outboundengine.com"))
        # TODO need to verify request.