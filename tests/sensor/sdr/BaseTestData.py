import unittest
from datetime import datetime

from weatherwatch.sensor.sdr.BaseData import BaseData

class BaseTestData(unittest.TestCase):

    def assertBase(self, expected, record: BaseData):

        self.assertEqual(datetime.strptime(expected[BaseData.TIME_KEY], BaseData.DATE_FORMAT), record.timeStamp)

        self.assertEqual(expected[BaseData.ID_KEY], record.id)
        self.assertEqual((expected[BaseData.BATTERY_KEY] == 1), record.batteryOk)
