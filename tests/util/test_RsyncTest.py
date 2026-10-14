import unittest

from util.Rsync import Rsync


class RsyncTest(unittest.TestCase):

    def test_archive_nonzero_returns_false(self):
        rsync = Rsync()
        rsync.BASE_CMD = ["python3", "-c", "import sys; sys.exit(3)"]
        self.assertFalse(rsync.archive("src", "dest"))

    def test_archive_timeout_returns_false(self):
        rsync = Rsync()
        rsync.BASE_CMD = ["python3", "-c", "import time; time.sleep(30)"]
        rsync.ARCHIVE_TIMEOUT = 0.2
        self.assertFalse(rsync.archive("src", "dest"))

    def test_archive_success_returns_true(self):
        rsync = Rsync()
        rsync.BASE_CMD = ["python3", "-c", "import sys; sys.exit(0)"]
        self.assertTrue(rsync.archive("src", "dest"))
