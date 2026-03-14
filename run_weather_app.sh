#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# Fix common macOS + conda Qt plugin conflict
unset QT_PLUGIN_PATH || true
unset QT_QPA_PLATFORM_PLUGIN_PATH || true

QT_PLUGINS_PATH="$(python3 -c 'import PyQt6, os; print(os.path.join(os.path.dirname(PyQt6.__file__), "Qt6", "plugins", "platforms"))')"
export QT_QPA_PLATFORM_PLUGIN_PATH="$QT_PLUGINS_PATH"

if [[ -z "${OPENWEATHER_API_KEY:-}" ]]; then
  echo "OPENWEATHER_API_KEY is not set."
  echo "Run: export OPENWEATHER_API_KEY=\"your_key_here\""
  exit 1
fi

python3 main.py
