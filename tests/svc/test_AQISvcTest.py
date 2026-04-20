import time
import unittest

import pytest

from entity.AQISensor import AQISensor
from repository.AQISensorRepository import AQISensorRepository
from svc.AQISvc import AQISvc


@pytest.mark.integration
class AQISvcTest(unittest.TestCase):
    """
    Integration tests for AQISvc against the live HM3301 sensor and database.

    Requires a physical HM3301 connected via I2C and a running MariaDB instance.
    Run with:  poetry run pytest -m integration tests/svc/test_AQISvcTest.py
    """

    def setup_method(self, test_method):
        self.svc: AQISvc = AQISvc()
        self.repo: AQISensorRepository = AQISensorRepository()
        self.repo.exec("truncate " + AQISensor.__tablename__)

    def teardown_method(self, test_method):
        AQISensorRepository().exec("truncate " + AQISensor.__tablename__)

    def test_process_reads_and_persists_data(self):
        for x in range(5):
            self.svc.process()
            time.sleep(0.5)

        act = self.repo.find_latest()
        self.assertIsNotNone(act)
