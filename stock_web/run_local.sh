#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT="${1:-8080}"

echo "[Stock Pilot] starting local server at http://127.0.0.1:${PORT}"
cd "$ROOT_DIR"
python3 -m http.server "$PORT"
