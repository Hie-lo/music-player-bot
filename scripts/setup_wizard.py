#!/usr/bin/env python3
"""Interactive local setup wizard.

All prompts run on the operator's machine. Secret inputs are hidden and written
only to .env with restrictive permissions. Nothing is sent to this agent.
"""

from __future__ import annotations

from getpass import getpass
import os
from pathlib import Path
import secrets
import shutil
import socket
import stat
import sys
from urllib.parse import quote_plus


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value or default


def ask_secret(prompt: str, default: str = "") -> str:
    suffix = " [configured; press Enter to keep]" if default else ""
    value = getpass(f"{prompt}{suffix}: ")
    return value or default


def ask_bool(prompt: str, default: bool = False) -> bool:
    suffix = "Y/n" if default else "y/N"
    value = input(f"{prompt} [{suffix}]: ").strip().lower()
    if not value:
        return default
    return value in {"y", "yes", "1", "true", "on"}


def parse_existing_env(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        values[key.strip()] = value
    return values


def port_is_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) != 0


def choose_port(prompt: str, default: int, max_attempts: int = 100) -> int:
    raw = ask(prompt, str(default))
    try:
        port = int(raw)
    except ValueError:
        print("Invalid port; using the default.")
        port = default
    if port_is_free(port):
        return port
    print(f"Port {port} is already in use.")
    for candidate in range(port + 1, port + max_attempts):
        if port_is_free(candidate):
            print(f"Using free port {candidate} instead.")
            return candidate
    raise RuntimeError("Could not find a free host port")


def write_env(values: dict[str, str]) -> None:
    if ENV_PATH.exists():
        backup = ENV_PATH.with_name(f".env.backup-{secrets.token_hex(4)}")
        shutil.copy2(ENV_PATH, backup)
        backup.chmod(stat.S_IRUSR | stat.S_IWUSR)
        print(f"Existing .env was backed up to {backup.name}; its contents were not displayed.")
    lines = [
        "# Generated locally by scripts/setup_wizard.py. Never commit this file.",
        *[f"{key}={value}" for key, value in values.items()],
        "",
    ]
    ENV_PATH.write_text("\n".join(lines), encoding="utf-8")
    ENV_PATH.chmod(stat.S_IRUSR | stat.S_IWUSR)


def main() -> int:
    print("Music Player Bot setup wizard")
    print("Secrets are entered locally, hidden where possible, and never printed.")
    print()

    existing = parse_existing_env(ENV_PATH)
    bot_token = ask_secret("BotFather BOT_TOKEN", existing.get("BOT_TOKEN", ""))
    if not bot_token:
        raise RuntimeError("BOT_TOKEN is required")

    api_id = ask("Telegram API_ID", existing.get("API_ID", ""))
    if not api_id.isdigit() or int(api_id) <= 0:
        raise RuntimeError("API_ID must be a positive integer")
    api_hash = ask_secret("Telegram API_HASH", existing.get("API_HASH", ""))
    if not api_hash:
        raise RuntimeError("API_HASH is required")

    db_mode = ask("Database mode (external/docker)", existing.get("SETUP_DB_MODE", "external")).lower()
    if db_mode not in {"external", "docker"}:
        raise RuntimeError("Database mode must be external or docker")

    if db_mode == "docker":
        db_host = "127.0.0.1"
        db_port = choose_port("PostgreSQL host port", int(existing.get("POSTGRES_HOST_PORT", "5431")))
        db_user = ask("PostgreSQL user", existing.get("POSTGRES_USER", "musicbot"))
        db_name = ask("PostgreSQL database", existing.get("POSTGRES_DB", "musicbot"))
        db_password = ask_secret("PostgreSQL password", existing.get("POSTGRES_PASSWORD", "musicbot"))
        redis_host = "127.0.0.1"
        redis_port = choose_port("Redis host port", int(existing.get("REDIS_HOST_PORT", "16379")))
    else:
        db_host = ask("PostgreSQL host", existing.get("POSTGRES_HOST", "127.0.0.1"))
        db_port = int(ask("PostgreSQL port", existing.get("POSTGRES_PORT", "5431")))
        db_user = ask("PostgreSQL user", existing.get("POSTGRES_USER", "musicbot"))
        db_name = ask("PostgreSQL database", existing.get("POSTGRES_DB", "musicbot"))
        db_password = ask_secret("PostgreSQL password", existing.get("POSTGRES_PASSWORD", ""))
        redis_host = ask("Redis host", existing.get("REDIS_HOST", "127.0.0.1"))
        redis_port = int(ask("Redis port", existing.get("REDIS_PORT", "16379")))

    if not db_password:
        raise RuntimeError("PostgreSQL password is required")

    youtube_key = ask_secret("Optional YouTube API key (Enter to skip)", existing.get("YOUTUBE_API_KEY", ""))
    spotify_id = ask("Optional Spotify Client ID (Enter to skip)", existing.get("SPOTIFY_CLIENT_ID", ""))
    spotify_secret = ask_secret(
        "Optional Spotify Client Secret (Enter to skip)", existing.get("SPOTIFY_CLIENT_SECRET", "")
    )
    spotify_redirect = ask("Optional Spotify Redirect URI (Enter to skip)", existing.get("SPOTIFY_REDIRECT_URI", ""))
    test_chat_id = ask("Optional Telegram test chat id (Enter to skip)", existing.get("TEST_CHAT_ID", ""))

    external = ask_bool("Enable external providers now?", False)
    video = ask_bool("Enable experimental video now?", False)

    database_url = (
        f"postgresql+asyncpg://{quote_plus(db_user)}:{quote_plus(db_password)}"
        f"@{db_host}:{db_port}/{quote_plus(db_name)}"
    )
    values = {
        "BOT_TOKEN": bot_token,
        "API_ID": api_id,
        "API_HASH": api_hash,
        "ASSISTANT_SESSION": existing.get("ASSISTANT_SESSION", ""),
        "ENVIRONMENT": existing.get("ENVIRONMENT", "development"),
        "LOG_LEVEL": existing.get("LOG_LEVEL", "INFO"),
        "FFMPEG_PATH": existing.get("FFMPEG_PATH", "ffmpeg"),
        "TEMP_MEDIA_DIR": existing.get("TEMP_MEDIA_DIR", "./runtime/media"),
        "MAX_TRACK_DURATION_SECONDS": existing.get("MAX_TRACK_DURATION_SECONDS", "7200"),
        "MAX_QUEUE_SIZE": existing.get("MAX_QUEUE_SIZE", "100"),
        "DATABASE_URL": database_url,
        "REDIS_URL": f"redis://{redis_host}:{redis_port}/0",
        "POSTGRES_HOST_PORT": str(db_port) if db_mode == "docker" else existing.get("POSTGRES_HOST_PORT", "5431"),
        "REDIS_HOST_PORT": str(redis_port) if db_mode == "docker" else existing.get("REDIS_HOST_PORT", "16379"),
        "POSTGRES_HOST": db_host,
        "POSTGRES_PORT": str(db_port),
        "POSTGRES_USER": db_user,
        "POSTGRES_DB": db_name,
        "POSTGRES_PASSWORD": db_password,
        "SETUP_DB_MODE": db_mode,
        "WEBHOOK_BASE_URL": existing.get("WEBHOOK_BASE_URL", ""),
        "WEBHOOK_SECRET": existing.get("WEBHOOK_SECRET", ""),
        "SPOTIFY_CLIENT_ID": spotify_id,
        "SPOTIFY_CLIENT_SECRET": spotify_secret,
        "SPOTIFY_REDIRECT_URI": spotify_redirect,
        "YOUTUBE_API_KEY": youtube_key,
        "TEST_CHAT_ID": test_chat_id,
        "ENABLE_EXTERNAL_PROVIDERS": "true" if external else "false",
        "ENABLE_VIDEO": "true" if video else "false",
    }
    write_env(values)
    print(".env created/updated securely.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, RuntimeError, ValueError) as exc:
        print(f"Setup stopped: {exc}", file=sys.stderr)
        raise SystemExit(2)
