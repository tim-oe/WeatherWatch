import time
import unittest
from datetime import datetime
from unittest.mock import patch

import pytest
from python_event_bus import EventBus
from sqlalchemy import create_engine

from conf.AppConfig import AppConfig
from entity.OutdoorSensor import OutdoorSensor
from repository.DataStore import DataStore
from repository.OutdoorSensorRepository import OutdoorSensorRepository
from spool.SpoolStore import SpoolStore
from svc.DBFlushSvc import DBFlushSvc

# Does not resolve. Exercises a refused name lookup rather than a patched exception.
_UNREACHABLE_HOST = "unknownhost"


@pytest.mark.db
class DataStoreTest(unittest.TestCase):

    def test_is_available(self):
        ds: DataStore = DataStore()
        self.assertTrue(ds.is_available())

    def test_pool_uses_size_and_overflow(self):
        ds: DataStore = DataStore()
        db = AppConfig().database
        self.assertEqual(db.pool_overflow, ds._engine.pool._max_overflow)
        self.assertEqual(db.pool_size, ds._engine.pool._pool.maxsize)

    def test_mark_online_fires_only_on_transition(self):
        ds: DataStore = DataStore()
        DBFlushSvc()
        ds._offline_until = None
        with patch("repository.DataStore.EventBus.call", wraps=EventBus.call) as mocked:
            ds.mark_online()
            ds._online_pool.submit(lambda: None).result(timeout=5)
            mocked.assert_not_called()

            ds.mark_offline()
            self.assertTrue(ds.is_offline())
            ds.mark_online()
            ds._online_pool.submit(lambda: None).result(timeout=5)
            mocked.assert_called_once_with(DataStore.ONLINE_EVENT)

            ds.mark_online()
            ds._online_pool.submit(lambda: None).result(timeout=5)
            mocked.assert_called_once_with(DataStore.ONLINE_EVENT)
        self.assertFalse(ds.is_offline())

    def test_unresolvable_host_is_unavailable_and_spools(self):
        ds: DataStore = DataStore()
        ds._offline_until = None
        original = ds._engine
        dead = create_engine(
            ds._db_config.url.set(host=_UNREACHABLE_HOST),
            pool_size=1,
            max_overflow=0,
            pool_pre_ping=True,
            connect_args={
                "connect_timeout": DataStore.CONNECT_TIMEOUT,
                "read_timeout": DataStore.READ_TIMEOUT,
                "write_timeout": DataStore.WRITE_TIMEOUT,
            },
        )
        ds._engine = dead
        try:
            started = time.monotonic()
            self.assertFalse(ds.is_available())
            self.assertLess(time.monotonic() - started, DataStore.CONNECT_TIMEOUT + 5)

            when = datetime(2099, 6, 1, 1, 2, 3)
            started = time.monotonic()
            OutdoorSensorRepository().insert(_outdoor(when))
            self.assertLess(time.monotonic() - started, DataStore.CONNECT_TIMEOUT + 5)
            self.assertTrue(ds.is_offline())
            self.assertTrue(SpoolStore().segments("outdoor_sensor"))
        finally:
            ds._engine = original
            with ds._state_lock:
                ds._offline_until = None
            dead.dispose()


def _outdoor(read_time: datetime) -> OutdoorSensor:
    entity = OutdoorSensor()
    entity.sensor_id = 4242
    entity.battery_ok = True
    entity.read_time = read_time
    entity.temperature_f = 70.5
    entity.humidity = 40
    entity.raw = {"rain_mm": 1.0}
    entity.pressure = 1013.25
    entity.rain_cum_mm = 1.0
    entity.rain_delta_mm = 0.0
    entity.wind_avg_m_s = 1.5
    entity.wind_max_m_s = 2.5
    entity.wind_dir_deg = 180
    entity.light_lux = 100
    entity.uv = 1.25
    return entity
