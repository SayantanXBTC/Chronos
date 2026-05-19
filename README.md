# Chronos

An interactive world history map. Scrub through time from 3000 BCE to 2026 CE and watch civilizations rise and fall. Click any empire to see its lineage, lifespan, and what else existed at the same time.

Stack: FastAPI, PostGIS, Next.js, MapLibre GL.

---

## Setup

**Requirements:** Docker, Python 3.12+, Node.js 20+

```bash
cp .env.example .env
make dev-build
make migrate
make seed
```

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
| `make dev` | Start services |
| `make dev-build` | Rebuild and start |
| `make stop` | Stop everything |
| `make migrate` | Run migrations |
| `make seed` | Load data |
| `make test` | Run tests |
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
infra/           Docker config
```
