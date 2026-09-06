#!/usr/bin/env bash
# Force-stop everything the native dev stack may have left running:
# api/web processes (by port) plus Postgres and Redis.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
source scripts/local/paths.sh

kill_port() {
  local port="$1" label="$2"
  local pid
  pid="$(lsof -ti "tcp:$port" -sTCP:LISTEN 2>/dev/null || true)"
  if [ -n "$pid" ]; then
    echo "[stop] killing $label on port $port (pid $pid)"
    kill $pid 2>/dev/null
  fi
}

kill_port 8000 api
kill_port 3000 web

scripts/local/redis.sh stop
scripts/local/pg.sh stop
