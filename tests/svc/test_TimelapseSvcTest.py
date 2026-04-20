import unittest
from subprocess import TimeoutExpired
from unittest.mock import MagicMock, patch

from svc.TimelapseSvc import TimelapseSvc


class TimelapseSvcTest(unittest.TestCase):
    def test(self):
        svc: TimelapseSvc = TimelapseSvc()
        svc.process()

    def test_process_timeout_kills_process(self):
        """When p.wait() raises TimeoutExpired, p.kill() must be called."""
        svc = TimelapseSvc()
        mock_proc = MagicMock()
        mock_proc.__enter__ = lambda s: mock_proc
        mock_proc.__exit__ = MagicMock(return_value=False)
        mock_proc.wait.side_effect = TimeoutExpired(cmd="test", timeout=60)

        with patch("svc.TimelapseSvc.Popen", return_value=mock_proc):
            svc.process()

        mock_proc.kill.assert_called_once()