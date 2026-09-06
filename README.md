# Chronos

An interactive world history map. Scrub through time from 3000 BCE to 2026 CE and watch civilizations rise and fall. Click any empire to see its lineage, lifespan, and what else existed at the same time.

Stack: FastAPI, PostGIS, Next.js, MapLibre GL. Runs entirely natively — no Docker.

---

## Setup

**Requirements:** Homebrew, Python 3.12+, Node.js 20+

```bash
brew install postgresql@18 postgis redis
cp .env.example .env
make dev-build   # first time only: creates venvs, installs deps, migrates + seeds the DB, starts everything
```

On later runs, just:

```bash
make dev    # starts Postgres, Redis, the API, and the web app
            # Ctrl+C stops the api/web servers — Postgres/Redis keep running for a fast restart
make stop   # full teardown: api, web, Postgres, and Redis
```

Don't run `make dev` in a second terminal while one is already running — it'll refuse to start if ports 8000/3000 are taken. Run `make stop` first if you need to restart from a clean slate.

Verify it's running:

```bash
curl http://localhost:8000/health
# {"status": "ok", "env": "development"}
```

---

## Years

Stored as signed integers. `-264` = 264 BCE, `117` = 117 CE. Year 0 does not exist.

---

## Commands

| Command | What it does |
|---------|-------------|
| `make dev` | Start Postgres, Redis, API, and web natively; Ctrl+C stops all of it |
| `make dev-build` | First-time setup (venvs, npm install), then `make dev` |
| `make stop` | Force-stop everything, e.g. if `dev` was left running elsewhere |
| `make services-status` | Check whether Postgres/Redis are running |
| `make migrate` | Run migrations (starts Postgres if needed) |
| `make seed` | Load data (starts Postgres if needed) |
| `make test` | Run tests against ephemeral, throwaway Postgres/Redis |
| `make lint` | Lint with ruff |

---

## Services

| Service | Port |
|---------|------|
| API | 8000 |
| PostgreSQL/PostGIS | 5432 |
| Redis | 6379 |

---

## Structure

```
apps/api/        FastAPI backend
apps/web/        Next.js frontend
packages/data/   Data ingestion pipeline
scripts/local/   Native (Docker-free) dev service scripts: Postgres, Redis, dev/stop/test
```
