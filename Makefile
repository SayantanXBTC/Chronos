.PHONY: dev dev-build stop services-status migrate seed seed-entity seed-dry test lint

# First-time (or after dependency changes) setup: create venvs / install
# node_modules, run migrations + seed the database, then start the stack.
# Safe to re-run any time (migrate and seed are both idempotent).
dev-build:
	python3 -m venv apps/api/.venv
	apps/api/.venv/bin/pip install --upgrade pip
	apps/api/.venv/bin/pip install -e "./apps/api[dev,ingest]"
	python3 -m venv packages/data/.venv
	packages/data/.venv/bin/pip install --upgrade pip
	packages/data/.venv/bin/pip install -e "./packages/data[dev]"
	cd apps/web && npm install
	$(MAKE) migrate
	$(MAKE) seed
	$(MAKE) dev

# Start Postgres+PostGIS, Redis, the API, and the web app natively.
# Ctrl+C stops the api/web servers; Postgres/Redis keep running (use `make
# stop` to take those down too). Refuses to start if 8000/3000 are already
# in use — don't run this in two terminals at once.
dev:
	scripts/local/dev.sh

# Full teardown: api, web, Postgres, and Redis. Use this when you're done
# for the session, or if `make dev` was left running / exited uncleanly.
stop:
	scripts/local/stop.sh

services-status:
	scripts/local/pg.sh status
	scripts/local/redis.sh status

migrate:
	scripts/local/pg.sh ensure
	cd apps/api && DATABASE_URL=postgresql+asyncpg://history:history@localhost:5432/history \
		.venv/bin/alembic upgrade head

seed:
	scripts/local/pg.sh ensure
	DATABASE_URL=postgresql://history:history@localhost:5432/history packages/data/.venv/bin/python -m data
	scripts/local/redis.sh ensure
	redis-cli -p 6379 flushall >/dev/null 2>&1 || true

seed-entity:
	scripts/local/pg.sh ensure
	DATABASE_URL=postgresql://history:history@localhost:5432/history packages/data/.venv/bin/python -m data --entity $(ENTITY)
	scripts/local/redis.sh ensure
	redis-cli -p 6379 flushall >/dev/null 2>&1 || true

seed-dry:
	scripts/local/pg.sh ensure
	DATABASE_URL=postgresql://history:history@localhost:5432/history packages/data/.venv/bin/python -m data --dry-run

test:
	scripts/local/test.sh

lint:
	cd apps/api && .venv/bin/ruff check app/ tests/
