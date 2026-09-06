#!/usr/bin/env bash
# Manage the native (Homebrew) PostGIS-enabled Postgres cluster used for local dev.
# Usage: scripts/local/pg.sh {ensure|start|stop|status}
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
source scripts/local/paths.sh

is_running() {
  "$PG_BIN/pg_ctl" -D "$PGDATA" status >/dev/null 2>&1
}

init_if_needed() {
  if [ ! -s "$PGDATA/PG_VERSION" ]; then
    echo "[pg] initializing cluster in $PGDATA"
    "$PG_BIN/initdb" -D "$PGDATA" -U "$POSTGRES_USER" -A trust --auth-local=trust --auth-host=trust >/dev/null
  fi
}

start() {
  init_if_needed
  if is_running; then
    echo "[pg] already running"
    return
  fi
  "$PG_BIN/pg_ctl" -D "$PGDATA" -l "$LOG_DIR/postgres.log" \
    -o "-p $PG_PORT -k $RUN_DIR -c listen_addresses=localhost" \
    start

  for _ in $(seq 1 30); do
    if "$PG_BIN/pg_isready" -h localhost -p "$PG_PORT" -U "$POSTGRES_USER" >/dev/null 2>&1; then
      break
    fi
    sleep 0.5
  done

  if ! "$PG_BIN/psql" -h localhost -p "$PG_PORT" -U "$POSTGRES_USER" -d postgres -tAc \
      "SELECT 1 FROM pg_database WHERE datname='$POSTGRES_DB'" | grep -q 1; then
    echo "[pg] creating database $POSTGRES_DB"
    "$PG_BIN/createdb" -h localhost -p "$PG_PORT" -U "$POSTGRES_USER" "$POSTGRES_DB"
  fi

  "$PG_BIN/psql" -h localhost -p "$PG_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -q -c \
    'CREATE EXTENSION IF NOT EXISTS postgis; CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'

  echo "[pg] up on localhost:$PG_PORT (db=$POSTGRES_DB)"
}

stop() {
  if is_running; then
    "$PG_BIN/pg_ctl" -D "$PGDATA" -m fast stop
  else
    echo "[pg] not running"
  fi
}

status() {
  is_running && echo "[pg] running" || echo "[pg] stopped"
}

case "${1:-}" in
  ensure) start ;;
  start) start ;;
  stop) stop ;;
  status) status ;;
  *) echo "usage: $0 {ensure|start|stop|status}" >&2; exit 1 ;;
esac
