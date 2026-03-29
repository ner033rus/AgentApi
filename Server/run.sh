#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

VENV="$ROOT/.venv"
if [[ ! -d "$VENV" ]]; then
  python3 -m venv "$VENV"
fi

# shellcheck source=/dev/null
source "$VENV/bin/activate"
pip install -q -r "$ROOT/requirements.txt"

export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

HOST="${AGENT_API_HOST:-0.0.0.0}"
PORT="${AGENT_API_PORT:-8765}"

exec uvicorn app.main:app --host "$HOST" --port "$PORT" --app-dir "$ROOT"
