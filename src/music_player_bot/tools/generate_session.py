"""Generate a Telegram Assistant StringSession locally.

Usage requires the optional Telegram dependency:
    pip install -e '.[telegram]'
    music-bot-session

The generated value is written to the local .env file and is never printed.
Run this only on a trusted machine. Never paste the session into chat or Git.
"""

from __future__ import annotations

import asyncio
from getpass import getpass
import os
from pathlib import Path
import stat
import sys

from music_player_bot.config import Settings, SettingsError


def _upsert_env(path: Path, key: str, value: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    replaced = False
    output: list[str] = []
    for line in lines:
        if line.startswith(f"{key}="):
            output.append(f"{key}={value}")
            replaced = True
        else:
            output.append(line)
    if not replaced:
        if output and output[-1] != "":
            output.append("")
        output.append(f"{key}={value}")
    path.write_text("\n".join(output) + "\n", encoding="utf-8")
    path.chmod(stat.S_IRUSR | stat.S_IWUSR)


def _read_api_credentials() -> tuple[int, str]:
    loaded = Settings.from_environment()
    api_id_raw = str(loaded.api_id) if loaded.api_id is not None else input(
        "Telegram API_ID (not logged): "
    ).strip()
    api_hash = loaded.api_hash or getpass("Telegram API_HASH (hidden): ").strip()
    try:
        api_id = int(api_id_raw)
    except ValueError as exc:
        raise SettingsError("API_ID must be an integer") from exc
    if api_id <= 0 or not api_hash:
        raise SettingsError("API_ID and API_HASH are required")
    return api_id, api_hash


async def _generate(api_id: int, api_hash: str, phone: str) -> str:
    try:
        from telethon import TelegramClient
        from telethon.errors import SessionPasswordNeededError
        from telethon.sessions import StringSession
    except ImportError as exc:
        raise SettingsError(
            "Telethon is not installed. Install optional dependencies with: "
            "python -m pip install -e '.[telegram]'"
        ) from exc

    client = TelegramClient(StringSession(), api_id, api_hash)
    await client.connect()
    try:
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            code = getpass("Telegram login code (hidden): ").strip()
            try:
                await client.sign_in(phone=phone, code=code)
            except Exception as exc:  # Telethon error types vary by version.
                if "password" not in str(exc).lower():
                    raise
                password = getpass("Telegram 2FA password (hidden): ").strip()
                await client.sign_in(password=password)
        return client.session.save()
    finally:
        await client.disconnect()


def main() -> int:
    try:
        api_id, api_hash = _read_api_credentials()
        phone = os.getenv("ASSISTANT_PHONE") or input("Assistant phone number: ").strip()
        if not phone:
            raise SettingsError("Assistant phone number is required")
        session = asyncio.run(_generate(api_id, api_hash, phone))
        env_path = Path(os.getenv("ENV_FILE", ".env")).resolve()
        _upsert_env(env_path, "API_ID", str(api_id))
        _upsert_env(env_path, "API_HASH", api_hash)
        _upsert_env(env_path, "ASSISTANT_SESSION", session)
        print(f"Assistant session written to {env_path}")
        print("The session value was intentionally not displayed. Keep this file private.")
        return 0
    except (SettingsError, KeyboardInterrupt) as exc:
        print(f"Session generation stopped: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
