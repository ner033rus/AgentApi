#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

swift build -c release

APP_NAME="AgentAPIMenuBar.app"
BIN=".build/release/AgentAPIMenuBar"

rm -rf "$APP_NAME"
mkdir -p "$APP_NAME/Contents/MacOS"
cp "$BIN" "$APP_NAME/Contents/MacOS/"
cp Resources/Info.plist "$APP_NAME/Contents/Info.plist"
chmod +x "$APP_NAME/Contents/MacOS/AgentAPIMenuBar"

echo "Готово: $(pwd)/$APP_NAME"
echo "Запуск: open \"$APP_NAME\""
