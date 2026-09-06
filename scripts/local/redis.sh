#!/usr/bin/env bash
# Manage the native (Homebrew) Redis instance used for local dev.
# Usage: scripts/local/redis.sh {ensure|start|stop|status}
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
source scripts/local/paths.sh

PIDFILE="$RUN_DIR/redis.pid"

is_running() {
  [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null
}

start() {
  if is_running; then
    echo "[redis] already running"
    return
  fi
  redis-server \
    --port "$REDIS_PORT" \
    --dir "$REDIS_DIR" \
    --daemonize yes \
    --pidfile "$PIDFILE" \
    --logfile "$LOG_DIR/redis.log" \
    --maxmemory 256mb \
    --maxmemory-policy allkeys-lru \
    --save ""

  for _ in $(seq 1 20); do
    if redis-cli -p "$REDIS_PORT" ping >/dev/null 2>&1; then
      echo "[redis] up on localhost:$REDIS_PORT"
      return
    fi
    sleep 0.25
  done
  echo "[redis] failed to start, check $LOG_DIR/redis.log" >&2
  exit 1
}

stop() {
  if is_running; then
    redis-cli -p "$REDIS_PORT" shutdown nosave >/dev/null 2>&1 || true
    rm -f "$PIDFILE"
  else
    echo "[redis] not running"
  fi
}

status() {
  is_running && echo "[redis] running" || echo "[redis] stopped"
}

case "${1:-}" in
  ensure) start ;;
  start) start ;;
  stop) stop ;;
  status) status ;;
  *) echo "usage: $0 {ensure|start|stop|status}" >&2; exit 1 ;;
esac
