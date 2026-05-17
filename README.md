# History Platform Backend

A spatial-temporal historical database platform for querying world state snapshots across centuries.

## Prerequisites

- **Docker & Docker Compose** (for running services)
- **Python 3.12+** (for local development)
- **Node.js 20+** (for frontend, if applicable)

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

This returns a GeoJSON FeatureCollection representing geopolitical boundaries at that time.

## Year Convention

Years are stored as signed integers:

- **Negative values** = BCE (Before Common Era)
- **Positive values** = CE (Common Era)
- **Year 0 does not exist** (jumps from -1 to 1)

Examples:
- `-264` = 264 BCE
- `117` = 117 CE

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
| Neo4j | 7474, 7687 | Entity relationship graph |

## Project Structure

- `apps/api/` — FastAPI backend (Python 3.12, SQLAlchemy 2.x async, Alembic, PostGIS, Redis)
- `packages/data/` — Data ingestion package (Shapely, Fiona, GeoPandas)
- `infra/docker-compose.yml` — Docker service definitions
- `data/` — GIS data storage

## Documentation

For additional documentation, see the `docs/` directory.
