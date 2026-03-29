#!/usr/bin/env bash
# Установка unit systemd для Debian/Ubuntu.
# Запуск: sudo ./install-debian-service.sh
# Перед этим: python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UNIT_DST="/etc/systemd/system/agent-api.service"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Запустите с sudo." >&2
  exit 1
fi

sed "s|/AgentAPI|$ROOT|g" "$ROOT/agent-api.service" >"$UNIT_DST"
systemctl daemon-reload
systemctl enable agent-api.service
echo "Установлено: $UNIT_DST"
echo "Запуск: sudo systemctl start agent-api"
echo "Статус: sudo systemctl status agent-api"
