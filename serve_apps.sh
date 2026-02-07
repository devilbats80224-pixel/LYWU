#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT="${1:-8787}"

cd "$BASE_DIR"

IP_ADDR="$(ipconfig getifaddr en0 2>/dev/null || true)"
if [[ -z "$IP_ADDR" ]]; then
  IP_ADDR="$(ipconfig getifaddr en1 2>/dev/null || true)"
fi

echo "Serving: $BASE_DIR"
echo "Port: $PORT"
if [[ -n "$IP_ADDR" ]]; then
  echo "Open on iPhone (same Wi-Fi): http://$IP_ADDR:$PORT/"
fi

echo "Press Ctrl+C to stop"
python3 -m http.server "$PORT"
