import smtplib
import unittest
from unittest.mock import MagicMock, patch

from util.Emailer import Emailer


def _emailer_with_disabled_config():
    """Return the Emailer singleton with email disabled."""
    emailer = Emailer()
    emailer._config = MagicMock()
    emailer._config.enable = False
    return emailer


def _emailer_with_enabled_config():
    """Return the Emailer singleton with email enabled and fake SMTP settings."""
    emailer = Emailer()
    emailer._config = MagicMock()
    emailer._config.enable = True
    emailer._config.from_email = "from@example.com"
    emailer._config.to_email = "to@example.com"
    emailer._config.smtp_host = "smtp.example.com"
    emailer._config.smtp_port = 465
    emailer._config.username = "user"
    emailer._config.password = "pass"
    return emailer


class EmailerTest(unittest.TestCase):

    # ------------------------------------------------------------------
    # send_error_notification — disabled: does nothing after logging
    # ------------------------------------------------------------------

    def test_send_error_notification_disabled_does_not_send(self):
        emailer = _emailer_with_disabled_config()
        with patch.object(emailer, "send_message") as mock_send:
            emailer.send_error_notification(ValueError("test"), "UnitTest")
        mock_send.assert_not_called()

    # ------------------------------------------------------------------
    # send_error_notification — enabled: calls build / send helpers
    # ------------------------------------------------------------------

    def test_send_error_notification_enabled_calls_send_message(self):
        emailer = _emailer_with_enabled_config()
        with patch.object(emailer, "send_message") as mock_send:
            emailer.send_error_notification(ValueError("boom"), "UnitTest")
        mock_send.assert_called_once()

    def test_send_error_notification_enabled_swallows_inner_exception(self):
        emailer = _emailer_with_enabled_config()
        with patch.object(emailer, "send_message", side_effect=Exception("smtp down")):
            # Must not propagate the inner exception
            emailer.send_error_notification(RuntimeError("original"), "UnitTest")

    # ------------------------------------------------------------------
    # build_message
    # ------------------------------------------------------------------

    def test_build_message_returns_mime_multipart(self):
        from email.mime.multipart import MIMEMultipart
        emailer = _emailer_with_enabled_config()
        msg = emailer.build_message("Test Subject", ValueError("something went wrong"))
        self.assertIsInstance(msg, MIMEMultipart)

    def test_build_message_sets_from_to_subject(self):
        emailer = _emailer_with_enabled_config()
        exc = ValueError("oops")
        msg = emailer.build_message("My Subject", exc)
        self.assertEqual("from@example.com", msg["From"])
        self.assertEqual("to@example.com", msg["To"])
        self.assertIn("My Subject", msg["Subject"])

    def test_build_message_body_contains_exception_type(self):
        emailer = _emailer_with_enabled_config()
        exc = TypeError("bad type")
        msg = emailer.build_message("Prefix", exc)
        payload = msg.get_payload()
        body_text = payload[0].get_payload() if isinstance(payload, list) else str(payload)
        self.assertIn("TypeError", body_text)

    # ------------------------------------------------------------------
    # build_attachement
    # ------------------------------------------------------------------

    def test_build_attachement_returns_mime_base(self):
        from email.mime.base import MIMEBase
        emailer = _emailer_with_enabled_config()
        part = emailer.build_attachement("Stack trace line 1\nStack trace line 2")
        self.assertIsInstance(part, MIMEBase)

    def test_build_attachement_has_content_disposition(self):
        emailer = _emailer_with_enabled_config()
        part = emailer.build_attachement("trace")
        self.assertIn("attachment", part.get("Content-Disposition", ""))

    def test_build_attachement_swallows_os_unlink_error(self):
        """os.unlink raising OSError in finally block must not propagate."""
        import os
        emailer = _emailer_with_enabled_config()
        with patch("os.unlink", side_effect=OSError("Permission denied")):
            part = emailer.build_attachement("trace data")
        self.assertIsNotNone(part)

    # ------------------------------------------------------------------
    # send_message — SMTP interactions mocked
    # ------------------------------------------------------------------

    def test_send_message_calls_smtp_ssl(self):
        emailer = _emailer_with_enabled_config()
        mock_server = MagicMock()
        with patch("smtplib.SMTP_SSL", return_value=mock_server) as mock_ssl:
            from email.mime.multipart import MIMEMultipart
            msg = MIMEMultipart()
            msg["From"] = "from@example.com"
            msg["To"] = "to@example.com"
            msg["Subject"] = "test"
            emailer.send_message(msg)
        mock_ssl.assert_called_once_with("smtp.example.com", 465)
        mock_server.ehlo.assert_called_once()
        mock_server.login.assert_called_once_with("user", "pass")
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()
