#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="${SOVIGEN_WEB_HOST:-0.0.0.0}"
PORT="${SOVIGEN_WEB_PORT:-8765}"
cd "$PROJECT_ROOT"

LAN_IP=""
if [[ "$HOST" == "0.0.0.0" ]]; then
  LAN_IP="$(python3 - <<'PY'
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    sock.connect(("192.0.2.1", 80))
    print(sock.getsockname()[0])
except OSError:
    pass
finally:
    sock.close()
PY
)"
fi

if python3 - "$PORT" <<'PY'
import sys
from urllib.request import urlopen

try:
    with urlopen(f"http://127.0.0.1:{sys.argv[1]}/", timeout=2) as response:
        raise SystemExit(0 if response.headers.get("Server", "").startswith("SovigenLocal/") else 1)
except Exception:
    raise SystemExit(1)
PY
then
  if [[ -n "$LAN_IP" ]]; then
    printf 'Sovigen studio is already running: http://%s:%s\n' "$LAN_IP" "$PORT"
  else
    printf 'Sovigen studio is already running on port %s.\n' "$PORT"
  fi
  exit 0
fi

if [[ "$HOST" == "0.0.0.0" ]]; then
  if [[ -n "$LAN_IP" ]]; then
    printf 'Open on this network: http://%s:%s\n' "$LAN_IP" "$PORT"
  else
    printf 'Studio listening on port %s; find this device LAN address to open it.\n' "$PORT"
  fi
fi

exec python3 -m sovigen.web --host "$HOST" --port "$PORT"
