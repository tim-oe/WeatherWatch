
from datetime import datetime
import unittest
from unittest import mock
from urllib.parse import ParseResult

from entity.IndoorSensor import IndoorSensor
from entity.OutdoorSensor import OutdoorSensor
from repository.IndoorSensorRepository import IndoorSensorRepository
from repository.OutdoorSensorRepository import OutdoorSensorRepository
from svc.WUSvc import WUSvc
from wu.WUClient import WUClient
from wu.WUData import WUData

class WuSvcTest(unittest.TestCase):

    def post(self, readTime: datetime, data: WUData, endPoint: ParseResult = WUClient.END_POINT_URL):
        self._read_time = readTime
        self._data = data  

    def setup_method(self, test_method):
        self.svc: WUSvc = WUSvc()
        self._outdoorRepo: OutdoorSensorRepository = OutdoorSensorRepository()
        self.indoorRepo: IndoorSensorRepository = IndoorSensorRepository()

        self._outdoorRepo.exec('truncate ' + OutdoorSensor.__tablename__)
        self._outdoorRepo.exec_file("sql/sample/outdoor_sensor.sql")

        self.indoorRepo.exec('truncate ' + IndoorSensor.__tablename__)
        self.indoorRepo.exec_file("sql/sample/indoor_sensor.sql")

    def teardown_class(self):
        IndoorSensorRepository().exec('truncate ' + IndoorSensor.__tablename__)
        OutdoorSensorRepository().exec('truncate ' + OutdoorSensor.__tablename__)

    # mock posting to it not actually posts to WU
    #@mock.patch.object(WUClient, 'post', post)
    def test(self):
        with mock.patch.object(WUClient, 'post', self.post):
            self.svc.process()

            self.assertIsNotNone(self._read_time)
            print(f"{self._read_time}")
            self.assertIsNotNone(self._data)
            print(f"{self._data}")

    def test_set_aqi_enabled_populates_data(self):
        """set_aqi should populate aqpm2_5 and aqpm10 when AQI is enabled."""
        from entity.AQISensor import AQISensor
        from wu.WUData import WUData
        from decimal import Decimal

        mock_aqi = mock.MagicMock(spec=AQISensor)
        mock_aqi.pm_2_5_conctrt_std = Decimal("12.5")
        mock_aqi.pm_1_0_conctrt_std = Decimal("8.3")

        self.svc._aqi_config = mock.MagicMock()
        self.svc._aqi_config.enable = True
        self.svc._aqi_repo = mock.MagicMock()
        self.svc._aqi_repo.find_latest.return_value = mock_aqi

        data = WUData(winddir=0, windspeedmph=Decimal("1"), windgustmph=Decimal("1"),
                      humidity=50, tempf=Decimal("70"), dailyrainin=Decimal("0"),
                      baromin=Decimal("29.9"), solarradiation=Decimal("1"),
                      uv=Decimal("1"), indoortempf=Decimal("68"), indoorhumidity=40,
                      dewptf=Decimal("60"))
        self.svc.set_aqi(data)

        self.svc._aqi_repo.find_latest.assert_called_once()

    def test_set_aqi_disabled_skips(self):
        """set_aqi should not call find_latest when AQI is disabled."""
        self.svc._aqi_config = mock.MagicMock()
        self.svc._aqi_config.enable = False
        self.svc._aqi_repo = mock.MagicMock()

        from wu.WUData import WUData
        from decimal import Decimal
        data = WUData(winddir=0, windspeedmph=Decimal("1"), windgustmph=Decimal("1"),
                      humidity=50, tempf=Decimal("70"), dailyrainin=Decimal("0"),
                      baromin=Decimal("29.9"), solarradiation=Decimal("1"),
                      uv=Decimal("1"), indoortempf=Decimal("68"), indoorhumidity=40,
                      dewptf=Decimal("60"))
        self.svc.set_aqi(data)

        self.svc._aqi_repo.find_latest.assert_not_called()

    def test_process_exception_sends_error_notification(self):
        """When process() raises an exception, send_error_notification must be called."""
        self.svc._outdoor_repo = mock.MagicMock()
        self.svc._outdoor_repo.find_latest.side_effect = Exception("DB error")
        self.svc._emailer = mock.MagicMock()

        self.svc.process()

        self.svc._emailer.send_error_notification.assert_called_once()
            
