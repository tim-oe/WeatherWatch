import sys
import types
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import patch

import pytest
from python_event_bus import EventBus
from sqlalchemy import DateTime, Numeric
from sqlalchemy.exc import DataError, OperationalError
from sqlalchemy.orm import Mapped, mapped_column

from entity.BaseEntity import BaseEntity
from entity.OutdoorSensor import OutdoorSensor
from repository.BaseRepository import BaseRepository
from repository.DataStore import DataStore
from repository.OutdoorSensorRepository import OutdoorSensorRepository
from svc.DBFlushSvc import DBFlushSvc


class Probe(BaseEntity):
    """throwaway entity used only by the extensibility test"""

    __tablename__ = "spool_ext_foo"
    __table_args__ = {"extend_existing": True}

    read_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    value: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)


class ProbeRepository(BaseRepository):
    """throwaway repository; the test points its module at repository.*"""

    drained = []

    def __init__(self):
        super().__init__(Probe)

    def after_drain(self, first_read_time):
        ProbeRepository.drained.append(first_read_time)


def _outdoor(read_time, cum, delta, sensor_id=4242):
    entity = OutdoorSensor()
    entity.sensor_id = sensor_id
    entity.battery_ok = True
    entity.read_time = read_time
    entity.temperature_f = 70.5
    entity.humidity = 40
    entity.raw = {"rain_mm": cum}
    entity.pressure = 1013.25
    entity.rain_cum_mm = cum
    entity.rain_delta_mm = delta
    entity.wind_avg_m_s = 1.5
    entity.wind_max_m_s = 2.5
    entity.wind_dir_deg = 180
    entity.light_lux = 100
    entity.uv = 1.25
    return entity


@pytest.mark.db
class DBFlushSvcTest(unittest.TestCase):

    def setUp(self):
        self.ds = DataStore()
        self.ds._offline_until = None
        self.repo = OutdoorSensorRepository()
        self.svc = DBFlushSvc()
        self.repo.exec("delete from outdoor_sensor where sensor_id in (4242, 4343)")
        ProbeRepository.drained = []

    def tearDown(self):
        self.ds._offline_until = None
        self.repo.exec("delete from outdoor_sensor where sensor_id in (4242, 4343)")
        Probe.__table__.drop(self.ds._engine, checkfirst=True)

    def test_drain_is_oldest_first_and_idempotent(self):
        first = datetime(2099, 6, 1, 12, 0, 0)
        second = datetime(2099, 6, 1, 12, 5, 0)
        self.ds.mark_offline()
        self.repo.insert(_outdoor(first, 1.5, 1.5))
        self.repo.insert(_outdoor(second, 2.5, 1.0))
        self.svc.process()
        self.ds._online_pool.submit(lambda: None).result(timeout=10)
        session = self.ds.session
        try:
            rows = (
                session.query(OutdoorSensor)
                .filter(OutdoorSensor.sensor_id == 4242)
                .order_by(OutdoorSensor.read_time.asc())
                .all()
            )
            self.assertEqual([first, second], [row.read_time for row in rows])
        finally:
            session.close()
        self.svc.process()
        session = self.ds.session
        try:
            rows_again = session.query(OutdoorSensor).filter(OutdoorSensor.sensor_id == 4242).all()
            self.assertEqual(2, len(rows_again))
        finally:
            session.close()

    def test_rejected_lines_and_import_guard(self):
        from spool.SpoolStore import SpoolStore

        store = SpoolStore()
        table = store._folder / "outdoor_sensor"
        table.mkdir(parents=True, exist_ok=True)
        bad = table / "20200101T00.jsonl"
        bad.write_text(
            "\n".join(
                [
                    '{"repository": "os.system.System", "entity": "OutdoorSensor", "data": {}}',
                    '{"repository": "repository.OutdoorSensorRepository.OutdoorSensorRepository", '
                    '"entity": "IndoorSensor", "data": {}}',
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        with patch("svc.DBFlushSvc.importlib.import_module", wraps=__import__("importlib").import_module) as importer:
            self.svc.process()
            imported = [call.args[0] for call in importer.call_args_list]
        self.assertNotIn("os.system", imported)
        rejected = (table / "rejected.jsonl").read_text(encoding="utf-8")
        self.assertIn("repository path rejected", rejected)
        self.assertIn("does not match", rejected)

    def test_unavailable_leaves_the_spool(self):
        from spool.SpoolStore import SpoolStore

        self.ds.mark_offline()
        self.repo.insert(_outdoor(datetime(2099, 6, 2, 1, 0, 0), 1.0, 0.0))
        with patch.object(DataStore, "is_available", return_value=False):
            self.svc.process()
        self.assertTrue(SpoolStore().segments("outdoor_sensor"))

    def test_periodic_probe_recovers_and_drains_without_a_live_write(self):
        from spool.SpoolStore import SpoolStore

        when = datetime(2099, 6, 2, 2, 0, 0)
        self.ds.mark_offline()
        self.repo.insert(_outdoor(when, 1.0, 0.0))
        with patch.object(self.ds, "mark_online", wraps=self.ds.mark_online) as mark_online:
            self.svc.process()
        mark_online.assert_called_once()
        self.assertFalse(SpoolStore().segments("outdoor_sensor"))
        session = self.ds.session
        try:
            count = session.query(OutdoorSensor).filter(OutdoorSensor.read_time == when).count()
        finally:
            session.close()
        self.assertEqual(1, count)

    def test_mid_drain_connection_failure_keeps_remainder_and_resumes(self):
        from spool.SpoolStore import SpoolStore

        first = datetime(2099, 6, 3, 1, 0)
        second = datetime(2099, 6, 3, 1, 5)
        self.ds.mark_offline()
        self.repo.insert(_outdoor(first, 1.0, 0.0))
        self.repo.insert(_outdoor(second, 2.0, 0.0))
        original = OutdoorSensorRepository.replay
        calls = 0

        def flaky(repo, entity):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OperationalError("insert", {}, Exception("down"))
            return original(repo, entity)

        with patch.object(OutdoorSensorRepository, "replay", flaky):
            self.svc.process()
        self.assertTrue(self.ds.is_offline())
        draining = list((SpoolStore()._folder / "outdoor_sensor").glob("*.jsonl.draining"))
        self.assertEqual(1, len(draining))
        self.assertEqual(1, len(draining[0].read_text(encoding="utf-8").splitlines()))

        self.svc.process()
        session = self.ds.session
        try:
            rows = session.query(OutdoorSensor).filter(OutdoorSensor.sensor_id == 4242).all()
        finally:
            session.close()
        self.assertEqual(2, len(rows))
        self.assertFalse(SpoolStore().segments("outdoor_sensor"))

    def test_reentrancy_lock_skips_overlapping_drain(self):
        self.assertTrue(self.svc._lock.acquire(blocking=False))
        try:
            with patch.object(DataStore, "is_available") as probe:
                self.svc.process()
            probe.assert_not_called()
        finally:
            self.svc._lock.release()

    def test_rain_delta_includes_live_row_and_after_drain_runs_once(self):
        start = datetime(2099, 7, 1, 8, 0, 0)
        self.repo.insert_direct(_outdoor(start, 10.0, 10.0))
        self.ds.mark_offline()
        self.repo.insert(_outdoor(datetime(2099, 7, 1, 8, 5, 0), 12.5, 0.0))
        self.repo.insert(_outdoor(datetime(2099, 7, 1, 8, 10, 0), 14.0, 0.0))
        self.ds._offline_until = datetime(2000, 1, 1, tzinfo=timezone.utc)
        calls = []
        original = OutdoorSensorRepository.after_drain

        def wrapped(repo, first):
            calls.append(first)
            return original(repo, first)

        with patch.object(OutdoorSensorRepository, "after_drain", wrapped):
            self.repo.insert(_outdoor(datetime(2099, 7, 1, 8, 15, 0), 15.25, 5.25))
            self.ds._online_pool.submit(lambda: None).result(timeout=10)
        self.assertEqual(1, len(calls))
        session = self.ds.session
        try:
            rows = (
                session.query(OutdoorSensor)
                .filter(OutdoorSensor.sensor_id == 4242)
                .order_by(OutdoorSensor.read_time.asc())
                .all()
            )
        finally:
            session.close()
        deltas = [row.rain_delta_mm for row in rows]
        self.assertEqual(
            [Decimal("10.00"), Decimal("2.50"), Decimal("1.50"), Decimal("1.25")],
            deltas,
        )

    def test_after_drain_failure_keeps_window_for_retry(self):
        from spool.SpoolStore import SpoolStore

        when = datetime(2099, 7, 2, 8, 0)
        self.ds.mark_offline()
        self.repo.insert(_outdoor(when, 3.0, 0.0))
        later_table = SpoolStore()._folder / "zz_after_drain"
        later_table.mkdir(parents=True, exist_ok=True)
        (later_table / "20200101T00.jsonl").write_text("not json\n", encoding="utf-8")
        with patch.object(OutdoorSensorRepository, "after_drain", side_effect=RuntimeError("fixup failed")):
            self.svc.process()
        self.assertEqual(when, SpoolStore().peek_window("outdoor_sensor")[0])
        self.assertTrue((later_table / "rejected.jsonl").is_file())
        self.assertFalse(SpoolStore().segments("zz_after_drain"))
        self.svc.process()
        self.assertEqual((None, None), SpoolStore().peek_window("outdoor_sensor"))

    def test_after_drain_tracks_each_outdoor_sensor_separately(self):
        start = datetime(2099, 7, 3, 8, 0)
        self.repo.insert_direct(_outdoor(start, 10.0, 10.0, sensor_id=4242))
        self.repo.insert_direct(_outdoor(start, 100.0, 100.0, sensor_id=4343))
        self.repo.insert_direct(_outdoor(datetime(2099, 7, 3, 8, 5), 12.0, 0.0, sensor_id=4242))
        self.repo.insert_direct(_outdoor(datetime(2099, 7, 3, 8, 6), 103.0, 0.0, sensor_id=4343))
        self.repo.after_drain(datetime(2099, 7, 3, 8, 5))
        session = self.ds.session
        try:
            rows = (
                session.query(OutdoorSensor)
                .filter(OutdoorSensor.read_time >= datetime(2099, 7, 3, 8, 5))
                .order_by(OutdoorSensor.sensor_id.asc())
                .all()
            )
        finally:
            session.close()
        self.assertEqual([Decimal("2.00"), Decimal("3.00")], [row.rain_delta_mm for row in rows])

    def test_event_drain_does_not_recurse(self):
        self.ds.mark_offline()
        self.repo.insert(_outdoor(datetime(2099, 8, 1, 9, 0, 0), 1.0, 1.0))
        with patch("repository.DataStore.EventBus.call", wraps=EventBus.call) as mocked:
            self.ds.mark_online()
            self.ds._online_pool.submit(lambda: None).result(timeout=10)
        self.assertEqual(1, mocked.call_count)
        session = self.ds.session
        try:
            count = session.query(OutdoorSensor).filter(OutdoorSensor.sensor_id == 4242).count()
        finally:
            session.close()
        self.assertEqual(1, count)

    def test_throwaway_repository_spools_and_replays(self):
        module = types.ModuleType("repository.spool_probe")
        sys.modules["repository.spool_probe"] = module
        ProbeRepository.__module__ = module.__name__
        ProbeRepository.__qualname__ = "ProbeRepository"
        module.ProbeRepository = ProbeRepository
        Probe.__table__.drop(self.ds._engine, checkfirst=True)
        Probe.__table__.create(self.ds._engine)

        when = datetime(2099, 9, 1, 10, 0, 0)
        entity = Probe()
        entity.read_time = when
        entity.value = 1.5
        self.ds.mark_offline()
        ProbeRepository().insert(entity)
        self.svc.process()
        self.ds._online_pool.submit(lambda: None).result(timeout=10)

        session = self.ds.session
        try:
            stored = session.query(Probe).filter(Probe.read_time == when).one()
        finally:
            session.close()
        self.assertEqual(Decimal("1.5"), stored.value)
        self.assertEqual([when], ProbeRepository.drained)


@pytest.mark.db
class OfflineRepositoryTest(unittest.TestCase):

    def setUp(self):
        self.ds = DataStore()
        self.ds._offline_until = None
        self.repo = OutdoorSensorRepository()
        self.repo.exec("delete from outdoor_sensor where sensor_id = 4242")

    def tearDown(self):
        self.ds._offline_until = None
        self.repo.exec("delete from outdoor_sensor where sensor_id = 4242")

    def test_known_offline_spools_without_a_connection(self):
        from spool.SpoolStore import SpoolStore

        when = datetime(2099, 5, 1, 1, 2, 3)
        self.ds.mark_offline()
        with patch.object(DataStore, "session", side_effect=AssertionError("session touched")):
            self.repo.insert(_outdoor(when, 4.5, 0.0))
        self.assertTrue(SpoolStore().segments("outdoor_sensor"))

    def test_connection_error_spools_and_marks_offline(self):
        from spool.SpoolStore import SpoolStore

        when = datetime(2099, 5, 2, 1, 2, 3)
        with patch(
            "repository.BaseRepository.Session.commit",
            side_effect=OperationalError("insert", {}, Exception("down")),
        ):
            self.repo.insert(_outdoor(when, 4.5, 0.0))
        self.assertTrue(self.ds.is_offline())
        self.assertTrue(SpoolStore().segments("outdoor_sensor"))

    def test_integrity_error_does_not_spool_or_mark_offline(self):
        from spool.SpoolStore import SpoolStore
        from sqlalchemy.exc import IntegrityError

        when = datetime(2099, 5, 3, 1, 2, 3)
        self.repo.insert(_outdoor(when, 1.0, 1.0))
        with self.assertRaises(IntegrityError):
            self.repo.insert(_outdoor(when, 2.0, 1.0))
        self.assertFalse(self.ds.is_offline())
        self.assertFalse(SpoolStore().segments("outdoor_sensor"))

    def test_data_error_does_not_spool_or_mark_offline(self):
        from spool.SpoolStore import SpoolStore

        with patch(
            "repository.BaseRepository.Session.commit",
            side_effect=DataError("insert", {}, Exception("bad value")),
        ), self.assertRaises(DataError):
            self.repo.insert(_outdoor(datetime(2099, 5, 4, 1, 2, 3), 1.0, 1.0))
        self.assertFalse(self.ds.is_offline())
        self.assertFalse(SpoolStore().segments("outdoor_sensor"))

    def test_read_short_circuits_when_offline(self):
        self.ds.mark_offline()
        with patch.object(DataStore, "session", side_effect=AssertionError("session touched")):
            self.assertIsNone(self.repo.find_latest())
            self.assertEqual([], self.repo.find_greater_than_read_time(datetime(2099, 1, 1)))
            self.assertEqual(Decimal("0"), self.repo.get_days_rainfall(datetime(2099, 1, 1).date()))

    def test_read_connection_error_marks_offline_and_returns_default(self):
        with patch(
            "repository.OutdoorSensorRepository.Session.query",
            side_effect=OperationalError("select", {}, Exception("down")),
        ):
            self.assertIsNone(self.repo.find_latest())
        self.assertTrue(self.ds.is_offline())
