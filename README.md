# Kleio

An interactive world history map where you scrub a timeline from 3000 BCE to 2026 CE and watch civilizations rise and fall in real time. Click any empire to explore its lineage, dates, and contemporaries. Built with FastAPI, PostGIS, and MapLibre GL.

## Prerequisites

- Docker and Docker Compose
- Python 3.12 or higher
- Node.js 20 or higher

## Quick Start

1. Copy environment file:
   ```bash
   cp .env.example .env
   ```

2. Build and start services:
   ```bash
   make dev-build
   ```

3. Run database migrations:
   ```bash
   make migrate
   ```

4. Seed initial data:
   ```bash
   make seed
   ```

## Verify Installation

Check that the API is running:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok", "env": "development"}
```

Query historical world state for 264 BCE at zoom level 4:

```bash
curl "http://localhost:8000/api/v1/world/state?year=-264&zoom=4"
```

## Year Convention

Years are stored as signed integers. Negative values represent BCE, positive values represent CE. Year 0 does not exist — the calendar jumps from -1 to 1.

## Development Commands

| Command | Purpose |
|---------|---------|
| `make dev` | Start services without rebuilding |
| `make dev-build` | Build and start services |
| `make stop` | Stop all services |
| `make migrate` | Run database migrations |
| `make seed` | Load initial data |
| `make test` | Run test suite |
| `make lint` | Check code style with ruff |

## Services

| Service | Port | Purpose |
|---------|------|---------|
| API | 8000 | FastAPI backend |
| PostgreSQL/PostGIS | 5432 | Spatial-temporal database |
| Redis | 6379 | World state cache |

## Project Structure

- `apps/api/` — FastAPI backend (Python 3.12, SQLAlchemy 2, Alembic, PostGIS, Redis)
- `apps/web/` — Next.js 14 frontend (MapLibre GL, Zustand, Tailwind CSS)
- `packages/data/` — Data ingestion pipeline (Shapely, Fiona, GeoPandas)
- `infra/docker-compose.yml` — Docker service definitions
