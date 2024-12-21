import unittest
from datetime import datetime

from weatherwatch.sensor.sdr.BaseData import BaseData

class BaseTestData(unittest.TestCase):

    def assertBase(self, expected, record: BaseData):

        self.assertEqual(datetime.strptime(expected[BaseData.TIME_KEY], BaseData.DATE_FORMAT), record.time_stamp)

        self.assertEqual(expected[BaseData.ID_KEY], record.sensor_id)
        self.assertEqual((expected[BaseData.BATTERY_KEY] == 1), record.battery_ok)
