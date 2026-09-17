#!/usr/bin/env bash
# Interactive, idempotent Linux setup for the project.
# It installs local prerequisites, creates .venv, writes .env safely and runs
# the local Assistant session generator. It never prints secrets.
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f pyproject.toml ]]; then
  cat >&2 <<'EOF'
This directory is not the project branch that contains pyproject.toml.
Run this first, after checking that you have no uncommitted work:

  git fetch origin arena/01a0af03-music-player-bot
  git switch arena/01a0af03-music-player-bot || git switch --track origin/arena/01a0af03-music-player-bot
  git pull --ff-only origin arena/01a0af03-music-player-bot

Then run: bash scripts/setup.sh
EOF
  exit 2
fi

if [[ "${EUID}" -ne 0 ]] && ! command -v sudo >/dev/null 2>&1; then
  echo "This setup needs root or sudo to install Linux packages." >&2
  exit 2
fi

ask_yes_no() {
  local prompt="$1"
  local default="${2:-y}"
  local suffix='[Y/n]'
  [[ "$default" == "n" ]] && suffix='[y/N]'
  local answer
  read -r -p "$prompt $suffix " answer
  answer="${answer:-$default}"
  case "$answer" in
    y|Y|yes|Yes|YES) return 0 ;;
    *) return 1 ;;
  esac
}

if command -v apt-get >/dev/null 2>&1; then
  if ask_yes_no "Install/update system packages (Python, FFmpeg, Git, curl)?" y; then
    export DEBIAN_FRONTEND=noninteractive
    if [[ "${EUID}" -eq 0 ]]; then
      apt-get update
      apt-get install -y python3 python3-venv python3-pip ffmpeg git curl ca-certificates
    else
      sudo apt-get update
      sudo apt-get install -y python3 python3-venv python3-pip ffmpeg git curl ca-certificates
    fi
  fi
else
  echo "apt-get was not found; install Python 3.11+, FFmpeg and Git manually." >&2
fi

PYTHON_BIN="${PYTHON_BIN:-python3}"
command -v "$PYTHON_BIN" >/dev/null 2>&1 || { echo "python3 is required." >&2; exit 2; }

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "FFmpeg is not available. Install it before the live Playback POC." >&2
  exit 2
fi

"$PYTHON_BIN" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[all]"

PYTHONPATH=src python scripts/setup_wizard.py

if [[ -f .env ]]; then
  echo
  echo "Configuration was written to .env with mode 600. Values were not printed."
fi

if grep -q '^SETUP_DB_MODE=docker$' .env 2>/dev/null; then
  if ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1; then
    echo "Docker Compose is required for the selected database mode."
    if command -v apt-get >/dev/null 2>&1 && ask_yes_no "Install Docker Engine and Compose from system packages?" y; then
      export DEBIAN_FRONTEND=noninteractive
      if [[ "${EUID}" -eq 0 ]]; then
        apt-get update
        apt-get install -y docker.io docker-compose-plugin || apt-get install -y docker.io docker-compose
      else
        sudo apt-get update
        sudo apt-get install -y docker.io docker-compose-plugin || sudo apt-get install -y docker.io docker-compose
      fi
      if command -v systemctl >/dev/null 2>&1; then
        systemctl enable --now docker || true
      fi
    fi
  fi

  if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    if ask_yes_no "Start this project's isolated PostgreSQL and Redis containers?" y; then
      docker compose up -d postgres redis
      docker compose ps
    fi
  elif command -v docker-compose >/dev/null 2>&1; then
    if ask_yes_no "Start this project's isolated PostgreSQL and Redis containers?" y; then
      docker-compose up -d postgres redis
      docker-compose ps
    fi
  else
    echo "Docker Compose is still unavailable; database containers were not started." >&2
  fi
fi

PYTHONPATH=src python -m music_player_bot.tools.check_runtime || true

echo
echo "Setup finished. The live Playback Proof of Concept is still required before production playback is declared."
