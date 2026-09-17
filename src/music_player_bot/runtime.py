"""Safe runtime prerequisite checks."""

from __future__ import annotations

from dataclasses import dataclass
import shutil

from .config import Settings


@dataclass(frozen=True, slots=True)
class RuntimeCheck:
    name: str
    ok: bool
    detail: str


def check_runtime(settings: Settings) -> list[RuntimeCheck]:
    checks = [
        RuntimeCheck("BOT_TOKEN", bool(settings.bot_token), "configured" if settings.bot_token else "missing"),
        RuntimeCheck("API_ID", settings.api_id is not None, "configured" if settings.api_id else "missing"),
        RuntimeCheck("API_HASH", bool(settings.api_hash), "configured" if settings.api_hash else "missing"),
        RuntimeCheck(
            "ASSISTANT_SESSION",
            bool(settings.assistant_session),
            "configured" if settings.assistant_session else "missing",
        ),
        RuntimeCheck(
            "FFMPEG",
            shutil.which(settings.ffmpeg_path) is not None,
            f"found: {settings.ffmpeg_path}" if shutil.which(settings.ffmpeg_path) else "not found",
        ),
    ]
    return checks


def all_ready(checks: list[RuntimeCheck]) -> bool:
    return all(check.ok for check in checks)
