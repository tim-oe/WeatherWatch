import json
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from conf.AppConfig import AppConfig
from entity.SolarReading import SolarReading
from entity.TemperatureReading import TemperatureReading
from mqtt.MqttListener import MqttListener
from repository.SolarReadingRepository import SolarReadingRepository
from repository.TemperatureReadingRepository import TemperatureReadingRepository


class MqttListenerTest(unittest.TestCase):

    def setup_method(self, test_method):
        self._solar_repo: SolarReadingRepository = SolarReadingRepository()
        self._temperature_repo: TemperatureReadingRepository = TemperatureReadingRepository()

        self._solar_repo.exec(f"truncate {self._solar_repo.entity.__table__}")
        self._temperature_repo.exec(f"truncate {self._temperature_repo.entity.__table__}")

    def teardown_class(self):
        solar_repo: SolarReadingRepository = SolarReadingRepository()
        solar_repo.exec(f"truncate {solar_repo.entity.__table__}")

        temperature_repo: TemperatureReadingRepository = TemperatureReadingRepository()
        temperature_repo.exec(f"truncate {temperature_repo.entity.__table__}")

    def test_handle_solar(self):
        listener: MqttListener = MqttListener()

        payload = {
            "type": "solar",
            "name": "solar",
            "read_time": datetime.now().isoformat(),
            "read_duration_ms": 150.25,
            "model": "RNG-CTRL-WND10",
            "device_id": 1,
            "battery_percentage": 85,
            "battery_voltage": 13.2,
            "battery_current": 1.50,
            "battery_temperature": 25,
            "battery_type": "lithium",
            "controller_temperature": 30,
            "charging_status": "mppt",
            "load_status": "on",
            "load_voltage": 12.1,
            "load_current": 0.80,
            "load_power": 10,
            "pv_voltage": 18.5,
            "pv_current": 2.10,
            "pv_power": 38,
            "battery_min_voltage_today": 12.0,
            "battery_max_voltage_today": 14.4,
            "max_charging_current_today": 3.50,
            "max_discharging_current_today": 1.20,
            "max_charging_power_today": 50,
            "max_discharging_power_today": 15,
            "charging_amp_hours_today": 12,
            "discharging_amp_hours_today": 8,
            "power_generation_today": 600.5,
            "power_consumption_today": 200.3,
            "power_generation_total": 150000,
        }

        listener._handle_solar(payload)

        act: SolarReading = self._solar_repo.find_latest()
        self.assertIsNotNone(act)
        self.assertIsNotNone(act.id)
        self.assertEqual("solar", act.name)
        self.assertEqual("mppt", act.charging_status)
        self.assertEqual(85, act.battery_percentage)
        self.assertEqual(150000, act.power_generation_total)

    def test_handle_solar_minimal(self):
        listener: MqttListener = MqttListener()

        payload = {
            "name": "solar",
            "battery_voltage": 13.2,
            "pv_voltage": 18.5,
        }

        listener._handle_solar(payload)

        act: SolarReading = self._solar_repo.find_latest()
        self.assertIsNotNone(act)
        self.assertIsNotNone(act.id)
        self.assertEqual("solar", act.type)
        self.assertIsNotNone(act.read_time)
        self.assertIsNone(act.charging_status)

    def test_handle_temperature(self):
        listener: MqttListener = MqttListener()

        payload = {
            "type": "temperature",
            "name": "battery_temp",
            "read_time": datetime.now().isoformat(),
            "read_duration_ms": 50.10,
            "value": 22.375,
            "unit": "C",
        }

        listener._handle_temperature(payload)

        act: TemperatureReading = self._temperature_repo.find_latest()
        self.assertIsNotNone(act)
        self.assertIsNotNone(act.id)
        self.assertEqual("battery_temp", act.name)
        self.assertEqual("C", act.unit)

    def test_handle_temperature_defaults(self):
        listener: MqttListener = MqttListener()

        payload = {
            "value": 18.5,
        }

        listener._handle_temperature(payload)

        act: TemperatureReading = self._temperature_repo.find_latest()
        self.assertIsNotNone(act)
        self.assertEqual("temperature", act.type)
        self.assertEqual("temperature", act.name)
        self.assertEqual("C", act.unit)
        self.assertIsNotNone(act.read_time)

    def test_on_message_solar(self):
        listener: MqttListener = MqttListener()
        config = AppConfig().mqtt

        msg = MagicMock()
        msg.topic = config.solar_topic
        msg.payload = json.dumps({
            "name": "solar",
            "battery_voltage": 12.8,
            "pv_voltage": 17.5,
        }).encode("utf-8")

        listener._on_message(None, None, msg)

        act: SolarReading = self._solar_repo.find_latest()
        self.assertIsNotNone(act)
        self.assertEqual("solar", act.name)

    def test_on_message_temperature(self):
        listener: MqttListener = MqttListener()
        config = AppConfig().mqtt

        msg = MagicMock()
        msg.topic = config.temperature_topic
        msg.payload = json.dumps({
            "name": "ambient",
            "value": 21.5,
            "unit": "C",
        }).encode("utf-8")

        listener._on_message(None, None, msg)

        act: TemperatureReading = self._temperature_repo.find_latest()
        self.assertIsNotNone(act)
        self.assertEqual("ambient", act.name)

    def test_on_message_bad_json(self):
        listener: MqttListener = MqttListener()
        config = AppConfig().mqtt

        msg = MagicMock()
        msg.topic = config.solar_topic
        msg.payload = b"not json"

        listener._on_message(None, None, msg)

        act: SolarReading = self._solar_repo.find_latest()
        self.assertIsNone(act)
