#!/usr/bin/env bash
# Start the full local stack natively (no Docker): Postgres, Redis, the FastAPI
# API, and the Next.js web app. Runs in the foreground. Ctrl+C stops the API
# and web app; Postgres/Redis are left running so the next `make dev` is fast.
# Use `make stop` for a full teardown including the databases.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
source scripts/local/paths.sh

API_VENV="apps/api/.venv"
WEB_DIR="apps/web"

if [ ! -x "$API_VENV/bin/uvicorn" ]; then
  echo "error: apps/api virtualenv missing. Run 'make dev-build' first." >&2
  exit 1
fi
if [ ! -d "$WEB_DIR/node_modules" ]; then
  echo "error: apps/web dependencies missing. Run 'make dev-build' first." >&2
  exit 1
fi

port_in_use() { lsof -ti "tcp:$1" -sTCP:LISTEN >/dev/null 2>&1; }

if port_in_use 8000 || port_in_use 3000; then
  echo "error: port 8000 or 3000 is already in use — is 'make dev' already running in another terminal?" >&2
  echo "       run 'make stop' first, or check with: lsof -i :8000 -i :3000" >&2
  exit 1
fi

scripts/local/pg.sh ensure
scripts/local/redis.sh ensure

API_PID=""
WEB_PID=""
TAIL_PID=""
CLEANED_UP=0

cleanup() {
  [ "$CLEANED_UP" = "1" ] && return
  CLEANED_UP=1
  echo ""
  echo "[dev] stopping api/web (postgres and redis keep running — use 'make stop' to stop them too)..."
  [ -n "$TAIL_PID" ] && kill "$TAIL_PID" 2>/dev/null
  [ -n "$WEB_PID" ] && kill "$WEB_PID" 2>/dev/null
  [ -n "$API_PID" ] && kill "$API_PID" 2>/dev/null
  wait 2>/dev/null
  echo "[dev] stopped"
}
trap cleanup INT TERM EXIT

(
  cd apps/api
  exec env DATABASE_URL="$DATABASE_URL" REDIS_URL="$REDIS_URL" \
    .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
) > "$LOG_DIR/api.log" 2>&1 &
API_PID=$!

(
  cd "$WEB_DIR"
  exec npm run dev
) > "$LOG_DIR/web.log" 2>&1 &
WEB_PID=$!

echo "[dev] api   -> http://localhost:8000  (log: $LOG_DIR/api.log)"
echo "[dev] web   -> http://localhost:3000  (log: $LOG_DIR/web.log)"
echo "[dev] pg    -> localhost:$PG_PORT"
echo "[dev] redis -> localhost:$REDIS_PORT"
echo "[dev] tailing logs — Ctrl+C to stop the api/web servers"
echo ""

tail -f "$LOG_DIR/api.log" "$LOG_DIR/web.log" &
TAIL_PID=$!

wait "$TAIL_PID"
