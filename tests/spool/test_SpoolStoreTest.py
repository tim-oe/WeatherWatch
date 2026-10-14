import shutil
import threading
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from spool.SpoolStore import SpoolCapacityError, SpoolStore


def _usage(free):
    return type("Usage", (), {"total": 100, "used": 100 - free, "free": free})()


class SpoolStoreTest(unittest.TestCase):

    def setUp(self):
        self.store = SpoolStore()
        self.store._evict_alerted = False
        self.store._age_alerted = False
        for child in self.store._folder.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()

    def test_hourly_rotation(self):
        with patch.object(self.store, "_segment_name", side_effect=["20260101T01.jsonl", "20260101T02.jsonl"]):
            self.store.append("alpha", '{"n": 1}')
            self.store.append("alpha", '{"n": 2}')
        names = [path.name for path in self.store.segments("alpha")]
        self.assertEqual(["20260101T01.jsonl", "20260101T02.jsonl"], names)

    def test_draining_is_adopted_and_appends_go_to_a_new_file(self):
        self.store.append("alpha", "seed")
        claimed = self.store.claim_oldest("alpha")
        self.assertTrue(claimed.name.endswith(".draining"))
        again = self.store.claim_oldest("alpha")
        self.assertEqual(claimed, again)
        self.store.append("alpha", "fresh")
        self.assertIn("seed", claimed.read_text(encoding="utf-8"))
        self.assertNotIn("fresh", claimed.read_text(encoding="utf-8"))
        restored = self.store.release(claimed)
        self.assertTrue(restored.name.endswith(".jsonl"))
        self.assertIn("seed", restored.read_text(encoding="utf-8"))

    def test_concurrent_appends_are_not_lost_across_claim(self):
        self.store.append("alpha", "seed")
        per_thread = 25

        def writer(index):
            for row in range(per_thread):
                self.store.append("alpha", f"row-{index}-{row}")

        threads = [threading.Thread(target=writer, args=(index,)) for index in range(4)]
        for thread in threads:
            thread.start()
        claimed = self.store.claim_oldest("alpha")
        for thread in threads:
            thread.join()
        lines = []
        if claimed is not None and claimed.exists():
            lines.extend(claimed.read_text(encoding="utf-8").splitlines())
        for path in self.store.segments("alpha"):
            lines.extend(path.read_text(encoding="utf-8").splitlines())
        self.assertEqual(1 + 4 * per_thread, len([line for line in lines if line.strip()]))

    def test_eviction_drops_oldest_and_spares_active_and_draining(self):
        alpha = self.store._folder / "alpha"
        beta = self.store._folder / "beta"
        alpha.mkdir(exist_ok=True)
        beta.mkdir(exist_ok=True)
        active_name = (datetime.now(timezone.utc) - timedelta(hours=1)).strftime("%Y%m%dT%H") + ".jsonl"
        (alpha / "20200101T00.jsonl").write_text("old\n", encoding="utf-8")
        (beta / "20200101T01.jsonl.draining").write_text("drain\n", encoding="utf-8")
        (beta / "20200101T02.jsonl").write_text("next\n", encoding="utf-8")
        (alpha / active_name).write_text("active\n", encoding="utf-8")
        with patch.object(self.store, "_segment_name", return_value=active_name), patch(
            "spool.SpoolStore.shutil.disk_usage", side_effect=[_usage(5), _usage(5), _usage(90), _usage(90)]
        ), patch("spool.SpoolStore.Emailer") as emailer:
            self.store.append("alpha", "incoming")
        self.assertFalse((alpha / "20200101T00.jsonl").exists())
        self.assertFalse((beta / "20200101T02.jsonl").exists())
        self.assertTrue((beta / "20200101T01.jsonl.draining").exists())
        active = (alpha / active_name).read_text(encoding="utf-8")
        self.assertIn("active", active)
        self.assertIn("incoming", active)
        emailer.return_value.send_alert.assert_called_once()

    def test_eviction_spares_current_segment_in_every_table(self):
        active_name = "20260101T01.jsonl"
        alpha = self.store._folder / "alpha"
        beta = self.store._folder / "beta"
        alpha.mkdir(exist_ok=True)
        beta.mkdir(exist_ok=True)
        (alpha / "20200101T00.jsonl").write_text("old\n", encoding="utf-8")
        beta_active = beta / active_name
        beta_active.write_text("current\n", encoding="utf-8")
        with patch.object(self.store, "_segment_name", return_value=active_name), patch(
            "spool.SpoolStore.shutil.disk_usage", side_effect=[_usage(5), _usage(90), _usage(90)]
        ):
            self.store.append("alpha", "incoming")
        self.assertTrue(beta_active.exists())
        self.assertEqual("current\n", beta_active.read_text(encoding="utf-8"))

    def test_append_fails_when_floor_cannot_be_preserved(self):
        active_name = "20260101T01.jsonl"
        alpha = self.store._folder / "alpha"
        alpha.mkdir(exist_ok=True)
        active = alpha / active_name
        active.write_text("current\n", encoding="utf-8")
        with patch.object(self.store, "_segment_name", return_value=active_name), patch(
            "spool.SpoolStore.shutil.disk_usage", return_value=_usage(5)
        ):
            with self.assertRaises(SpoolCapacityError):
                self.store.append("alpha", "incoming")
        self.assertEqual("current\n", active.read_text(encoding="utf-8"))

    def test_window_metadata_update_is_atomic_and_keeps_earliest(self):
        table = self.store._folder / "alpha"
        table.mkdir(exist_ok=True)
        later = datetime(2026, 1, 1, 2, 0)
        earlier = datetime(2026, 1, 1, 1, 0)
        self.store.remember_read_time("alpha", "repository.Later", later)
        self.store.remember_read_time("alpha", "repository.Earlier", earlier)
        self.store.remember_read_time("alpha", "repository.Ignored", later)
        self.assertEqual((earlier, "repository.Later"), self.store.peek_window("alpha"))
        self.assertFalse((table / ".window_start.tmp").exists())

    def test_interrupted_window_replace_preserves_previous_metadata(self):
        table = self.store._folder / "alpha"
        table.mkdir(exist_ok=True)
        saved = datetime(2026, 1, 1, 2, 0)
        self.store.remember_read_time("alpha", "repository.Saved", saved)
        with patch("spool.SpoolStore.os.replace", side_effect=OSError("power loss")):
            with self.assertRaises(OSError):
                self.store.remember_read_time("alpha", "repository.New", datetime(2026, 1, 1, 1, 0))
        self.assertEqual((saved, "repository.Saved"), self.store.peek_window("alpha"))

    def test_age_alert_latches_until_the_spool_is_empty(self):
        alpha = self.store._folder / "alpha"
        alpha.mkdir(exist_ok=True)
        (alpha / "20200101T00.jsonl").write_text("old\n", encoding="utf-8")
        with patch("spool.SpoolStore.shutil.disk_usage", return_value=_usage(90)), patch(
            "spool.SpoolStore.Emailer"
        ) as emailer:
            self.store.append("alpha", "a")
            self.store.append("alpha", "b")
            self.assertEqual(1, emailer.return_value.send_alert.call_count)
            shutil.rmtree(alpha)
            self.store.reset_alerts_if_empty()
            alpha.mkdir()
            (alpha / "20200101T00.jsonl").write_text("old\n", encoding="utf-8")
            self.store.append("alpha", "c")
        self.assertEqual(2, emailer.return_value.send_alert.call_count)
