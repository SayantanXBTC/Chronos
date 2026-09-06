# Shared paths/config for native (non-Docker) local dev services.
# Sourced by the other scripts in scripts/local/ — not meant to be run directly.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

LOCAL_DIR="$ROOT_DIR/.local"
PGDATA="$LOCAL_DIR/pgdata"
REDIS_DIR="$LOCAL_DIR/redis"
RUN_DIR="$LOCAL_DIR/run"
LOG_DIR="$LOCAL_DIR/log"

PG_PORT="${PG_PORT:-5432}"
REDIS_PORT="${REDIS_PORT:-6379}"

POSTGRES_DB="${POSTGRES_DB:-history}"
POSTGRES_USER="${POSTGRES_USER:-history}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-history}"

DATABASE_URL="postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:${PG_PORT}/${POSTGRES_DB}"
REDIS_URL="redis://localhost:${REDIS_PORT}"

mkdir -p "$PGDATA" "$REDIS_DIR" "$RUN_DIR" "$LOG_DIR" 2>/dev/null

PG_PREFIX="$(brew --prefix postgresql@18 2>/dev/null || brew --prefix postgresql 2>/dev/null)"
if [ -z "$PG_PREFIX" ]; then
  echo "error: postgresql not found via Homebrew. Run: brew install postgresql@18 postgis" >&2
  exit 1
fi
PG_BIN="$PG_PREFIX/bin"
