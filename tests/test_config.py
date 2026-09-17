from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from music_player_bot.config import Settings, SettingsError
from music_player_bot.runtime import all_ready, check_runtime


class SettingsTests(unittest.TestCase):
    def test_defaults_are_safe_and_secrets_are_not_in_summary(self) -> None:
        settings = Settings.from_mapping({})
        summary = settings.safe_summary()
        self.assertFalse(summary["bot_token_configured"])
        self.assertFalse(summary["assistant_session_configured"])
        self.assertEqual(settings.max_queue_size, 100)
        self.assertNotIn("api_hash", summary)
        self.assertNotIn("assistant_session", summary)

    def test_api_id_must_be_positive_integer(self) -> None:
        with self.assertRaises(SettingsError):
            Settings.from_mapping({"API_ID": "not-an-int"})
        with self.assertRaises(SettingsError):
            Settings.from_mapping({"API_ID": "0"})

    def test_boolean_values_are_strict(self) -> None:
        settings = Settings.from_mapping({"ENABLE_VIDEO": "yes"})
        self.assertTrue(settings.enable_video)
        with self.assertRaises(SettingsError):
            Settings.from_mapping({"ENABLE_VIDEO": "maybe"})

    def test_dotenv_is_loaded_without_printing_secret(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env"
            path.write_text(
                "BOT_TOKEN=local-secret\nAPI_ID=123\nAPI_HASH=hash\nDATABASE_URL=postgresql+asyncpg://u:p@127.0.0.1:5431/db\n",
                encoding="utf-8",
            )
            settings = Settings.from_environment(path)
            self.assertEqual(settings.api_id, 123)
            self.assertTrue(settings.bot_token)
            self.assertIn(":5431/", settings.database_url)
            self.assertNotIn("bot_token", repr(settings))

    def test_runtime_checks_do_not_expose_values(self) -> None:
        settings = Settings.from_mapping({"BOT_TOKEN": "secret", "API_ID": "123"})
        checks = check_runtime(settings)
        self.assertFalse(all_ready(checks))
        rendered = " ".join(f"{check.name}:{check.detail}" for check in checks)
        self.assertNotIn("secret", rendered)


if __name__ == "__main__":
    unittest.main()
