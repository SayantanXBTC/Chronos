#!/usr/bin/env bash
# Spin up ephemeral Postgres+PostGIS and Redis instances for the API test
# suite (separate ports/data dirs from the dev stack), run pytest, tear down.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
source scripts/local/paths.sh

TEST_PG_PORT=5433
TEST_REDIS_PORT=6380
TEST_PGDATA="$LOCAL_DIR/pgdata_test"
TEST_REDIS_DIR="$LOCAL_DIR/redis_test"
TEST_PG_RUN="$LOCAL_DIR/run_test"
TEST_REDIS_PIDFILE="$TEST_PG_RUN/redis.pid"

mkdir -p "$TEST_PGDATA" "$TEST_REDIS_DIR" "$TEST_PG_RUN"

cleanup() {
  echo "[test] tearing down ephemeral services"
  redis-cli -p "$TEST_REDIS_PORT" shutdown nosave >/dev/null 2>&1 || true
  "$PG_BIN/pg_ctl" -D "$TEST_PGDATA" -m immediate stop >/dev/null 2>&1 || true
  rm -rf "$TEST_PGDATA" "$TEST_REDIS_DIR" "$TEST_PG_RUN"
}
trap cleanup EXIT

if [ ! -s "$TEST_PGDATA/PG_VERSION" ]; then
  "$PG_BIN/initdb" -D "$TEST_PGDATA" -U history -A trust --auth-local=trust --auth-host=trust >/dev/null
fi
"$PG_BIN/pg_ctl" -D "$TEST_PGDATA" -l "$LOG_DIR/postgres_test.log" \
  -o "-p $TEST_PG_PORT -k $TEST_PG_RUN -c listen_addresses=localhost" start

for _ in $(seq 1 30); do
  "$PG_BIN/pg_isready" -h localhost -p "$TEST_PG_PORT" -U history >/dev/null 2>&1 && break
  sleep 0.5
done
"$PG_BIN/createdb" -h localhost -p "$TEST_PG_PORT" -U history history_test
"$PG_BIN/psql" -h localhost -p "$TEST_PG_PORT" -U history -d history_test -q -c \
  'CREATE EXTENSION IF NOT EXISTS postgis; CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'

redis-server --port "$TEST_REDIS_PORT" --dir "$TEST_REDIS_DIR" --daemonize yes \
  --pidfile "$TEST_REDIS_PIDFILE" --logfile "$LOG_DIR/redis_test.log" --save ""
for _ in $(seq 1 20); do
  redis-cli -p "$TEST_REDIS_PORT" ping >/dev/null 2>&1 && break
  sleep 0.25
done

cd apps/api
DATABASE_URL="postgresql+asyncpg://history:history@localhost:$TEST_PG_PORT/history_test" \
  REDIS_URL="redis://localhost:$TEST_REDIS_PORT" \
  .venv/bin/pytest tests/ -v
