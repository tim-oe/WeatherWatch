import unittest
from datetime import datetime

from src.sensor.sdr.BaseData import BaseData

class BaseTestData(unittest.TestCase):
    
    def assertBase(self, expected, record: BaseData):
        
        self.assertEqual(
            datetime.strptime(expected[BaseData.TIME_KEY], BaseData.DATE_FORMAT),
            record.timeStamp)

        self.assertEqual(expected[BaseData.MODEL_KEY],record.model)
        self.assertEqual(expected[BaseData.ID_KEY],record.id)
        self.assertEqual((expected[BaseData.BATTERY_KEY] == 1),record.batteryOk)
        self.assertEqual(expected[BaseData.MIC_KEY],record.mic)
        self.assertEqual(expected[BaseData.MOD_KEY],record.mod)
        self.assertEqual(expected[BaseData.FREQ_KEY],record.freq)
        self.assertEqual(expected[BaseData.RSSI_KEY],record.rssi)
        self.assertEqual(expected[BaseData.NOISE_KEY],record.noise)
        self.assertEqual(expected[BaseData.SNR_KEY],record.snr)
        