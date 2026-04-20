import json
import unittest

from sensor.sdr.IndoorData import IndoorData
from tests.sensor.sdr.BaseTestData import BaseTestData


class IndoorDataTest(BaseTestData):

    def test(self):
        with open("tests/data/indoor.json", "r") as file:
            expected = json.load(file)

        with open("tests/data/indoor.json", "r") as file:
            record: IndoorData = json.load(file, object_hook=IndoorData.json_decoder)

        self.assertBase(expected, record)
        self.assertEqual(expected[IndoorData.CHANNEL_KEY], record.channel)
        self.assertEqual(expected[IndoorData.HUMID_KEY], record.humidity)
        self.assertEqual(expected[IndoorData.TEMP_KEY], record.temperature)

    def test_json_decoder_invalid_data_raises(self):
        """Missing required key should cause json_decoder to raise Exception."""
        with self.assertRaises(Exception):
            IndoorData.json_decoder({"model": "test"})  # missing required keys

    def test_base_decoder_invalid_raises(self):
        """Malformed raw dict should cause base_decoder to raise Exception."""
        from sensor.sdr.BaseData import BaseData
        with self.assertRaises(Exception):
            BaseData.base_decoder(IndoorData(), {"bad": "data"})

    def test_base_data_key_without_channel(self):
        """key() without channel key produces correct bracket string."""
        from sensor.sdr.BaseData import BaseData
        raw = {BaseData.MODEL_KEY: "TestModel", BaseData.ID_KEY: 42}
        result = BaseData.key(raw)
        self.assertEqual("[TestModel|42]", result)

    def test_base_data_key_with_channel(self):
        """key() with channel key includes channel in bracket string."""
        from sensor.sdr.BaseData import BaseData
        raw = {BaseData.MODEL_KEY: "TestModel", BaseData.ID_KEY: 42, BaseData.CHANNEL_KEY: 3}
        result = BaseData.key(raw)
        self.assertEqual("[TestModel|42|3]", result)

    def test_base_data_property_getters(self):
        """Access model, mic, mod, freq, rssi, snr, noise, config getters on a decoded record."""
        with open("tests/data/indoor.json", "r") as file:
            record: IndoorData = json.load(file, object_hook=IndoorData.json_decoder)
        self.assertIsNotNone(record.model)
        self.assertIsNotNone(record.mic)
        self.assertIsNotNone(record.mod)
        self.assertIsNotNone(record.freq)
        # rssi, snr, noise may be None in sample data — just access them
        _ = record.rssi
        _ = record.snr
        _ = record.noise
        _ = record.config
