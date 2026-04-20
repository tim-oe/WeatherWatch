import os
import unittest
from unittest.mock import patch

from conf.EmailConfig import EmailConfig

_DISABLED_CFG = {
    "enable": False,
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 465,
    "username": "user@example.com",
    "password": "secret",
    "from_email": "from@example.com",
    "to_email": "to@example.com",
}

_ENABLED_CFG = {
    "enable": True,
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 465,
    "username": "user@example.com",
    "password": "secret",
    "from_email": "from@example.com",
    "to_email": "to@example.com",
}

_VALID_ENV = {"WW_EMAIL_USERNAME": "user", "WW_EMAIL_PASSWORD": "pass"}


class EmailConfigTest(unittest.TestCase):

    # ------------------------------------------------------------------
    # Disabled path — no env-var or validation checks required
    # ------------------------------------------------------------------

    def test_disabled_enable_is_false(self):
        cfg = EmailConfig(_DISABLED_CFG)
        self.assertFalse(cfg.enable)

    def test_disabled_property_host(self):
        cfg = EmailConfig(_DISABLED_CFG)
        self.assertEqual("smtp.gmail.com", cfg.host)

    def test_disabled_property_port(self):
        cfg = EmailConfig(_DISABLED_CFG)
        self.assertEqual(465, cfg.port)

    def test_disabled_property_username(self):
        cfg = EmailConfig(_DISABLED_CFG)
        self.assertEqual("user@example.com", cfg.username)

    def test_disabled_property_password(self):
        cfg = EmailConfig(_DISABLED_CFG)
        self.assertEqual("secret", cfg.password)

    def test_disabled_property_from_email(self):
        cfg = EmailConfig(_DISABLED_CFG)
        self.assertEqual("from@example.com", cfg.from_email)

    def test_disabled_property_to_email(self):
        cfg = EmailConfig(_DISABLED_CFG)
        self.assertEqual("to@example.com", cfg.to_email)

    # ------------------------------------------------------------------
    # Enabled path — happy path
    # ------------------------------------------------------------------

    @patch.dict(os.environ, _VALID_ENV)
    def test_enabled_with_valid_config(self):
        cfg = EmailConfig(_ENABLED_CFG)
        self.assertTrue(cfg.enable)
        self.assertEqual("from@example.com", cfg.from_email)
        self.assertEqual("to@example.com", cfg.to_email)

    @patch.dict(os.environ, _VALID_ENV)
    def test_enabled_properties_accessible(self):
        cfg = EmailConfig(_ENABLED_CFG)
        self.assertEqual("smtp.gmail.com", cfg.host)
        self.assertEqual(465, cfg.port)
        self.assertEqual("user@example.com", cfg.username)
        self.assertEqual("secret", cfg.password)

    # ------------------------------------------------------------------
    # Enabled path — missing env vars
    # ------------------------------------------------------------------

    def test_enabled_missing_both_env_vars_raises(self):
        clean_env = {k: v for k, v in os.environ.items()
                     if k not in (EmailConfig.USERNAME_ENVAR, EmailConfig.PASSWORD_ENVAR)}
        with patch.dict(os.environ, clean_env, clear=True):
            with self.assertRaises(Exception) as ctx:
                EmailConfig(_ENABLED_CFG)
        self.assertIn(EmailConfig.USERNAME_ENVAR, str(ctx.exception))

    # ------------------------------------------------------------------
    # Enabled path — invalid email addresses
    # ------------------------------------------------------------------

    @patch.dict(os.environ, _VALID_ENV)
    def test_enabled_invalid_to_email_raises(self):
        cfg_data = dict(_ENABLED_CFG, to_email="not-an-email")
        with self.assertRaises(Exception) as ctx:
            EmailConfig(cfg_data)
        self.assertIn("to email", str(ctx.exception).lower())

    @patch.dict(os.environ, _VALID_ENV)
    def test_enabled_invalid_from_email_raises(self):
        cfg_data = dict(_ENABLED_CFG, from_email="not-an-email")
        with self.assertRaises(Exception) as ctx:
            EmailConfig(cfg_data)
        self.assertIn("from email", str(ctx.exception).lower())
