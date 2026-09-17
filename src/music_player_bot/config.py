"""Runtime configuration with strict, secret-safe validation.

This module intentionally uses the standard library so the Session Generator and
configuration checks can run before optional Telegram/database dependencies exist.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Mapping


class SettingsError(ValueError):
    """Raised when required configuration is missing or malformed."""


_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}


def _env(mapping: Mapping[str, str], name: str, default: str | None = None) -> str | None:
    value = mapping.get(name, default)
    if value is None:
        return None
    value = value.strip()
    return value or None


def _required(mapping: Mapping[str, str], name: str) -> str:
    value = _env(mapping, name)
    if not value:
        raise SettingsError(f"Missing required environment variable: {name}")
    return value


def _integer(mapping: Mapping[str, str], name: str, default: int) -> int:
    value = _env(mapping, name)
    if value is None:
        return default
    try:
        parsed = int(value)
    except ValueError as exc:
        raise SettingsError(f"{name} must be an integer") from exc
    if parsed < 0:
        raise SettingsError(f"{name} must not be negative")
    return parsed


def _boolean(mapping: Mapping[str, str], name: str, default: bool = False) -> bool:
    value = _env(mapping, name)
    if value is None:
        return default
    normalized = value.lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    raise SettingsError(f"{name} must be one of: true, false, 1, 0, yes, no, on, off")


@dataclass(frozen=True, slots=True)
class Settings:
    """Validated settings; secret fields are hidden from repr and safe output."""

    bot_token: str | None = field(default=None, repr=False)
    api_id: int | None = None
    api_hash: str | None = field(default=None, repr=False)
    assistant_session: str | None = field(default=None, repr=False)
    environment: str = "development"
    log_level: str = "INFO"
    ffmpeg_path: str = "ffmpeg"
    temp_media_dir: Path = Path("./runtime/media")
    max_track_duration_seconds: int = 7200
    max_queue_size: int = 100
    database_url: str = "postgresql+asyncpg://musicbot:musicbot@localhost:5432/musicbot"
    redis_url: str = "redis://localhost:6379/0"
    webapp_base_url: str | None = None
    webhook_base_url: str | None = None
    webhook_secret: str | None = field(default=None, repr=False)
    spotify_client_id: str | None = field(default=None, repr=False)
    spotify_client_secret: str | None = field(default=None, repr=False)
    youtube_api_key: str | None = field(default=None, repr=False)
    enable_external_providers: bool = False
    enable_video: bool = False
    enable_mini_app: bool = False

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, str] | None = None) -> "Settings":
        values = os.environ if mapping is None else mapping
        api_id_raw = _env(values, "API_ID")
        api_id: int | None = None
        if api_id_raw is not None:
            try:
                api_id = int(api_id_raw)
            except ValueError as exc:
                raise SettingsError("API_ID must be an integer") from exc
            if api_id <= 0:
                raise SettingsError("API_ID must be positive")

        return cls(
            bot_token=_env(values, "BOT_TOKEN"),
            api_id=api_id,
            api_hash=_env(values, "API_HASH"),
            assistant_session=_env(values, "ASSISTANT_SESSION"),
            environment=_env(values, "ENVIRONMENT", "development") or "development",
            log_level=(_env(values, "LOG_LEVEL", "INFO") or "INFO").upper(),
            ffmpeg_path=_env(values, "FFMPEG_PATH", "ffmpeg") or "ffmpeg",
            temp_media_dir=Path(_env(values, "TEMP_MEDIA_DIR", "./runtime/media") or "./runtime/media"),
            max_track_duration_seconds=_integer(values, "MAX_TRACK_DURATION_SECONDS", 7200),
            max_queue_size=_integer(values, "MAX_QUEUE_SIZE", 100),
            database_url=_env(
                values,
                "DATABASE_URL",
                "postgresql+asyncpg://musicbot:musicbot@localhost:5432/musicbot",
            )
            or "",
            redis_url=_env(values, "REDIS_URL", "redis://localhost:6379/0") or "",
            webapp_base_url=_env(values, "WEBAPP_BASE_URL"),
            webhook_base_url=_env(values, "WEBHOOK_BASE_URL"),
            webhook_secret=_env(values, "WEBHOOK_SECRET"),
            spotify_client_id=_env(values, "SPOTIFY_CLIENT_ID"),
            spotify_client_secret=_env(values, "SPOTIFY_CLIENT_SECRET"),
            youtube_api_key=_env(values, "YOUTUBE_API_KEY"),
            enable_external_providers=_boolean(values, "ENABLE_EXTERNAL_PROVIDERS"),
            enable_video=_boolean(values, "ENABLE_VIDEO"),
            enable_mini_app=_boolean(values, "ENABLE_MINI_APP"),
        )

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls.from_mapping()

    def require_bot_runtime(self) -> None:
        """Validate values needed by the Bot Gateway without exposing them."""
        missing = [
            name
            for name, value in (
                ("BOT_TOKEN", self.bot_token),
                ("API_ID", self.api_id),
                ("API_HASH", self.api_hash),
            )
            if not value
        ]
        if missing:
            raise SettingsError("Missing bot runtime settings: " + ", ".join(missing))

    def require_assistant_runtime(self) -> None:
        """Validate values needed by the Assistant/Voice service."""
        self.require_bot_runtime()
        if not self.assistant_session:
            raise SettingsError("Missing assistant runtime setting: ASSISTANT_SESSION")

    def safe_summary(self) -> dict[str, object]:
        """Return diagnostics that are safe to put in a log."""
        return {
            "environment": self.environment,
            "log_level": self.log_level,
            "api_id_configured": self.api_id is not None,
            "bot_token_configured": bool(self.bot_token),
            "assistant_session_configured": bool(self.assistant_session),
            "ffmpeg_path": self.ffmpeg_path,
            "temp_media_dir": str(self.temp_media_dir),
            "database_configured": bool(self.database_url),
            "redis_configured": bool(self.redis_url),
            "external_providers_enabled": self.enable_external_providers,
            "video_enabled": self.enable_video,
            "mini_app_enabled": self.enable_mini_app,
        }
