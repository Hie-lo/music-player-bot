"""Print a secret-safe runtime readiness report."""

from __future__ import annotations

import sys

from music_player_bot.config import Settings, SettingsError
from music_player_bot.runtime import all_ready, check_runtime


def main() -> int:
    try:
        settings = Settings.from_environment()
    except SettingsError as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2

    checks = check_runtime(settings)
    for check in checks:
        marker = "OK" if check.ok else "BLOCKED"
        print(f"[{marker}] {check.name}: {check.detail}")

    if not all_ready(checks):
        print("Runtime is not ready for the live Playback Proof of Concept.", file=sys.stderr)
        return 2
    print("Runtime prerequisites are present. Live Telegram POC is still required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
