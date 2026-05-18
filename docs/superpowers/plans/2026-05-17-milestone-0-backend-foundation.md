# Milestone 0: Backend Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the complete foundational backend infrastructure for the temporal world-state engine — Docker stack, PostGIS schema, FastAPI service, Redis caching, and data ingestion pipeline with Rome + Han China seed data.

**Architecture:** Monorepo with a Python/FastAPI backend (`apps/api`) and a data ingestion package (`packages/data`). PostGIS stores temporal geometries, Neo4j stores entity relationships, Redis caches world-state responses. All historical years stored as integers (negative = BCE, no year 0).

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.x, Alembic, PostGIS 16-3.4, Redis 7, Neo4j 5, Shapely, Fiona, GeoPandas, pytest, Docker Compose.

---

## File Map

```
history-platform/
├── apps/
│   └── api/
│       ├── Dockerfile
│       ├── pyproject.toml
│       ├── alembic.ini
│       ├── alembic/
│       │   ├── env.py
│       │   └── versions/
│       │       └── 0001_initial_schema.py
│       ├── app/
│       │   ├── __init__.py
│       │   ├── main.py                  # FastAPI app factory
│       │   ├── config.py                # Settings via pydantic-settings
│       │   ├── database.py              # SQLAlchemy engine + session
│       │   ├── cache.py                 # Redis client + helpers
│       │   ├── models/
│       │   │   ├── __init__.py
│       │   │   ├── entity.py            # Entity, EntityName ORM models
│       │   │   ├── territory.py         # Territory ORM model
│       │   │   ├── event.py             # Event, EventEntity ORM models
│       │   │   └── layer.py             # Layer, LayerFeature ORM models
│       │   ├── schemas/
│       │   │   ├── __init__.py
│       │   │   ├── world.py             # WorldStateResponse, Feature Pydantic schemas
│       │   │   └── entity.py            # EntityDetail, EntityTimeline schemas
│       │   ├── routers/
│       │   │   ├── __init__.py
│       │   │   ├── world.py             # GET /world/state, /world/snapshots
│       │   │   ├── entities.py          # GET /entities/{slug}
│       │   │   └── events.py            # GET /events/
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   ├── world_state.py       # WorldState(year, bbox, zoom) logic
│       │   │   └── cache_service.py     # Cache read/write helpers
│       │   └── utils/
│       │       ├── __init__.py
│       │       └── year.py              # year_to_display(), display_to_year()
│       └── tests/
│           ├── conftest.py              # pytest fixtures (test DB, test client)
│           ├── test_year_utils.py
│           ├── test_world_state.py
│           ├── test_cache_service.py
│           └── test_routers.py
├── packages/
│   └── data/
│       ├── __init__.py
│       ├── ingest.py                    # CLI entry point: python -m data.ingest
│       ├── normalize.py                 # Geometry normalization utilities
│       ├── entity_map.py                # Source name → entity slug mapping
│       ├── snapshots.py                 # Precompute snapshot JSON files
│       ├── sources/
│       │   ├── __init__.py
│       │   ├── base.py                  # Abstract source parser
│       │   └── manual.py                # Hand-coded GeoJSON for Rome + Han MVP
│       └── tests/
│           ├── conftest.py
│           ├── test_normalize.py
│           └── test_entity_map.py
├── data/
│   ├── raw/                             # Source GIS files (gitignored if large)
│   ├── processed/                       # Normalized GeoJSON ready for import
│   └── snapshots/                       # Precomputed year snapshots
│       └── political/
│           └── {year}.geojson           # e.g., -264.geojson
├── infra/
│   ├── docker-compose.yml
│   ├── docker-compose.test.yml          # Isolated test DB
│   └── postgres/
│       └── init.sql                     # Enable PostGIS extension
├── .env.example
├── .env                                 # gitignored
├── Makefile                             # make dev, make test, make seed, make migrate
└── README.md
```

---

## Task 1: Monorepo Scaffold + Docker Compose

**Files:**
- Create: `infra/docker-compose.yml`
- Create: `infra/docker-compose.test.yml`
- Create: `infra/postgres/init.sql`
- Create: `.env.example`
- Create: `.env`
- Create: `Makefile`

- [ ] **Step 1: Create root directory structure**

```bash
mkdir -p apps/api packages/data data/raw data/processed data/snapshots/political infra/postgres
```

- [ ] **Step 2: Create PostGIS init script**

Create `infra/postgres/init.sql`:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

- [ ] **Step 3: Create docker-compose.yml**

Create `infra/docker-compose.yml`:

```yaml
version: "3.9"

services:
  postgres:
    image: postgis/postgis:16-3.4
    container_name: history_postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-history}
      POSTGRES_USER: ${POSTGRES_USER:-history}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-history}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infra/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-history}"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: history_redis
    ports:
      - "6379:6379"
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  neo4j:
    image: neo4j:5
    container_name: history_neo4j
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD:-history}
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data

  api:
    build:
      context: ./apps/api
      dockerfile: Dockerfile
    container_name: history_api
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-history}:${POSTGRES_PASSWORD:-history}@postgres:5432/${POSTGRES_DB:-history}
      REDIS_URL: redis://redis:6379
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_PASSWORD: ${NEO4J_PASSWORD:-history}
    ports:
      - "8000:8000"
    volumes:
      - ./apps/api:/app
      - ./data:/data
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
  neo4j_data:
```

- [ ] **Step 4: Create test docker-compose (isolated DB)**

Create `infra/docker-compose.test.yml`:

```yaml
version: "3.9"

services:
  postgres_test:
    image: postgis/postgis:16-3.4
    container_name: history_postgres_test
    environment:
      POSTGRES_DB: history_test
      POSTGRES_USER: history
      POSTGRES_PASSWORD: history
    ports:
      - "5433:5432"
    volumes:
      - ./infra/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    tmpfs:
      - /var/lib/postgresql/data

  redis_test:
    image: redis:7-alpine
    container_name: history_redis_test
    ports:
      - "6380:6379"
```

- [ ] **Step 5: Create .env.example**

Create `.env.example`:

```bash
# PostgreSQL
POSTGRES_DB=history
POSTGRES_USER=history
POSTGRES_PASSWORD=history

# Redis
REDIS_URL=redis://localhost:6379

# Neo4j
NEO4J_PASSWORD=history
NEO4J_URI=bolt://localhost:7687

# FastAPI
API_ENV=development
LOG_LEVEL=INFO

# Mapbox (frontend only, not used by API)
NEXT_PUBLIC_MAPBOX_TOKEN=pk.your_token_here
```

- [ ] **Step 6: Create .env from example**

```bash
cp .env.example .env
```

- [ ] **Step 7: Create Makefile**

Create `Makefile`:

```makefile
.PHONY: dev stop migrate seed test lint

dev:
	docker compose -f infra/docker-compose.yml up

dev-build:
	docker compose -f infra/docker-compose.yml up --build

stop:
	docker compose -f infra/docker-compose.yml down

migrate:
	docker compose -f infra/docker-compose.yml exec api alembic upgrade head

seed:
	docker compose -f infra/docker-compose.yml exec api python -m data.ingest

test:
	docker compose -f infra/docker-compose.test.yml up -d
	cd apps/api && DATABASE_URL=postgresql+asyncpg://history:history@localhost:5433/history_test REDIS_URL=redis://localhost:6380 pytest tests/ -v
	docker compose -f infra/docker-compose.test.yml down

lint:
	cd apps/api && ruff check app/ tests/
```

- [ ] **Step 8: Verify Docker stack starts**

```bash
docker compose -f infra/docker-compose.yml up postgres redis -d
docker compose -f infra/docker-compose.yml exec postgres psql -U history -c "SELECT PostGIS_Version();"
```

Expected output: PostGIS version string like `3.4 USE_GEOS=1 ...`

- [ ] **Step 9: Commit**

```bash
git init
git add infra/ .env.example Makefile
git commit -m "feat: docker compose stack with postgis, redis, neo4j"
```

---

## Task 2: FastAPI App Structure + Config

**Files:**
- Create: `apps/api/Dockerfile`
- Create: `apps/api/pyproject.toml`
- Create: `apps/api/app/__init__.py`
- Create: `apps/api/app/main.py`
- Create: `apps/api/app/config.py`

- [ ] **Step 1: Create Dockerfile**

Create `apps/api/Dockerfile`:

```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libgdal-dev gdal-bin \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Create pyproject.toml**

Create `apps/api/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "history-api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "sqlalchemy[asyncio]>=2.0",
    "asyncpg>=0.29",
    "alembic>=1.13",
    "geoalchemy2>=0.15",
    "pydantic-settings>=2.4",
    "redis>=5.0",
    "shapely>=2.0",
    "fiona>=1.9",
    "geopandas>=1.0",
    "orjson>=3.10",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "httpx>=0.27",
    "ruff>=0.6",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
```

- [ ] **Step 3: Create config.py**

Create `apps/api/app/config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://history:history@localhost:5432/history"
    redis_url: str = "redis://localhost:6379"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_password: str = "history"
    api_env: str = "development"
    log_level: str = "INFO"


settings = Settings()
```

- [ ] **Step 4: Create app/main.py**

Create `apps/api/app/main.py`:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import create_tables
from app.routers import entities, events, world


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="History Platform API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(world.router, prefix="/api/v1/world", tags=["world"])
app.include_router(entities.router, prefix="/api/v1/entities", tags=["entities"])
app.include_router(events.router, prefix="/api/v1/events", tags=["events"])


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.api_env}
```

- [ ] **Step 5: Write health check test**

Create `apps/api/tests/conftest.py`:

```python
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
```

Create `apps/api/tests/test_routers.py`:

```python
import pytest


async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

- [ ] **Step 6: Create stub router files**

Create `apps/api/app/routers/__init__.py` (empty).

Create `apps/api/app/routers/world.py`:

```python
from fastapi import APIRouter

router = APIRouter()


@router.get("/state")
async def get_world_state():
    return {"message": "not implemented"}


@router.get("/snapshots")
async def get_snapshots():
    return {"snapshots": []}
```

Create `apps/api/app/routers/entities.py`:

```python
from fastapi import APIRouter

router = APIRouter()


@router.get("/{slug}")
async def get_entity(slug: str):
    return {"slug": slug}
```

Create `apps/api/app/routers/events.py`:

```python
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_events():
    return {"events": []}
```

- [ ] **Step 7: Install deps and run health check**

```bash
cd apps/api
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

In another terminal:
```bash
curl http://localhost:8000/health
```

Expected: `{"status":"ok","env":"development"}`

- [ ] **Step 8: Run tests**

```bash
cd apps/api
pytest tests/test_routers.py -v
```

Expected: `test_health PASSED`

- [ ] **Step 9: Commit**

```bash
git add apps/api/
git commit -m "feat: fastapi app scaffold with health check"
```

---

## Task 3: Database Connection + Alembic Setup

**Files:**
- Create: `apps/api/app/database.py`
- Create: `apps/api/alembic.ini`
- Create: `apps/api/alembic/env.py`

- [ ] **Step 1: Create database.py**

Create `apps/api/app/database.py`:

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

- [ ] **Step 2: Write DB connection test**

Add to `apps/api/tests/test_routers.py`:

```python
async def test_db_connects(client):
    # Verifies the DB URL is parseable and engine creates without error
    from app.database import engine
    async with engine.connect() as conn:
        result = await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        assert result.scalar() == 1
```

> Note: This test requires PostGIS running. Skip in CI without DB by marking:  
> `@pytest.mark.skipif(os.getenv("CI_NO_DB") == "1", reason="no DB in CI")`

- [ ] **Step 3: Initialize Alembic**

```bash
cd apps/api
alembic init alembic
```

- [ ] **Step 4: Configure alembic.ini**

Edit `apps/api/alembic.ini`, set:

```ini
script_location = alembic
sqlalchemy.url = postgresql://history:history@localhost:5432/history
```

> Note: alembic.ini uses sync URL (no `+asyncpg`). Alembic runs synchronously for migrations.

- [ ] **Step 5: Configure alembic/env.py**

Replace `apps/api/alembic/env.py` with:

```python
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.database import Base
# Import all models so Base.metadata is populated
import app.models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url():
    url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
    # Alembic needs sync driver
    return url.replace("+asyncpg", "")


def run_migrations_offline():
    url = get_url()
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    cfg = config.get_section(config.config_ini_section, {})
    cfg["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(cfg, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 6: Create app/models/__init__.py**

Create `apps/api/app/models/__init__.py`:

```python
from app.models.entity import Entity, EntityName
from app.models.territory import Territory
from app.models.event import Event, EventEntity
from app.models.layer import Layer, LayerFeature

__all__ = ["Entity", "EntityName", "Territory", "Event", "EventEntity", "Layer", "LayerFeature"]
```

> Note: models don't exist yet — we create them in Task 4. Leave this file as a stub for now:

```python
# populated in Task 4
```

- [ ] **Step 7: Verify Alembic connects**

```bash
cd apps/api
DATABASE_URL=postgresql://history:history@localhost:5432/history alembic current
```

Expected: `INFO [alembic.runtime.migration] Context impl PostgresqlImpl.`

- [ ] **Step 8: Commit**

```bash
git add apps/api/app/database.py apps/api/alembic.ini apps/api/alembic/
git commit -m "feat: sqlalchemy async engine + alembic configured"
```

---

## Task 4: ORM Models + Initial Migration

**Files:**
- Create: `apps/api/app/models/entity.py`
- Create: `apps/api/app/models/territory.py`
- Create: `apps/api/app/models/event.py`
- Create: `apps/api/app/models/layer.py`
- Modify: `apps/api/app/models/__init__.py`
- Create: `apps/api/alembic/versions/0001_initial_schema.py`

- [ ] **Step 1: Write model tests first**

Create `apps/api/tests/test_models.py`:

```python
import pytest
from sqlalchemy import text

from app.database import engine


async def test_entities_table_exists():
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_name = 'entities'")
        )
        assert result.scalar() == "entities"


async def test_territories_has_geom_column():
    async with engine.connect() as conn:
        result = await conn.execute(
            text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'territories' AND column_name = 'geom'
            """)
        )
        assert result.scalar() == "geom"


async def test_territory_temporal_query():
    """Verify the canonical temporal WHERE clause works syntactically."""
    async with engine.connect() as conn:
        result = await conn.execute(
            text("""
                SELECT COUNT(*) FROM territories
                WHERE year_start <= :year AND (year_end IS NULL OR year_end > :year)
            """),
            {"year": -264}
        )
        assert result.scalar() == 0  # empty DB, zero rows, no error
```

Run to confirm they FAIL (tables don't exist yet):
```bash
cd apps/api && pytest tests/test_models.py -v
```
Expected: all 3 FAIL with `UndefinedTable` or similar.

- [ ] **Step 2: Create entity.py model**

Create `apps/api/app/models/entity.py`:

```python
import uuid

from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    color: Mapped[str | None] = mapped_column(String(7))  # hex color

    names: Mapped[list["EntityName"]] = relationship(back_populates="entity")
    territories: Mapped[list["Territory"]] = relationship(back_populates="entity")  # type: ignore[name-defined]


class EntityName(Base):
    __tablename__ = "entity_names"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en")
    year_start: Mapped[int] = mapped_column(nullable=False)
    year_end: Mapped[int | None] = mapped_column(nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True)

    entity: Mapped["Entity"] = relationship(back_populates="names", foreign_keys=[entity_id])
```

- [ ] **Step 3: Create territory.py model**

Create `apps/api/app/models/territory.py`:

```python
import uuid

from geoalchemy2 import Geometry
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Territory(Base):
    __tablename__ = "territories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    geom: Mapped[bytes] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False
    )
    simplified_geom: Mapped[bytes | None] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=True
    )
    year_start: Mapped[int] = mapped_column(nullable=False)
    year_end: Mapped[int | None] = mapped_column(nullable=True)
    confidence: Mapped[str] = mapped_column(String(20), default="approximate")
    source: Mapped[str | None] = mapped_column(Text, nullable=True)

    entity: Mapped["Entity"] = relationship(back_populates="territories", foreign_keys=[entity_id])  # type: ignore[name-defined]
```

- [ ] **Step 4: Create event.py model**

Create `apps/api/app/models/event.py`:

```python
import uuid

from geoalchemy2 import Geometry
from sqlalchemy import ARRAY, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    year_start: Mapped[int] = mapped_column(nullable=False)
    year_end: Mapped[int | None] = mapped_column(nullable=True)
    magnitude: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    geom: Mapped[bytes | None] = mapped_column(Geometry(srid=4326), nullable=True)
    layer: Mapped[str] = mapped_column(String(50), default="political")
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class EventEntity(Base):
    __tablename__ = "event_entities"

    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    role: Mapped[str | None] = mapped_column(String(50), nullable=True)
```

- [ ] **Step 5: Create layer.py model**

Create `apps/api/app/models/layer.py`:

```python
import uuid

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Layer(Base):
    __tablename__ = "layers"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class LayerFeature(Base):
    __tablename__ = "layer_features"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    layer_id: Mapped[str] = mapped_column(String(50), nullable=False)
    geom: Mapped[bytes] = mapped_column(Geometry(srid=4326), nullable=False)
    year_start: Mapped[int] = mapped_column(nullable=False)
    year_end: Mapped[int | None] = mapped_column(nullable=True)
    properties: Mapped[dict] = mapped_column(JSONB, default=dict)
```

- [ ] **Step 6: Update models/__init__.py**

Replace `apps/api/app/models/__init__.py`:

```python
from app.models.entity import Entity, EntityName
from app.models.territory import Territory
from app.models.event import Event, EventEntity
from app.models.layer import Layer, LayerFeature

__all__ = ["Entity", "EntityName", "Territory", "Event", "EventEntity", "Layer", "LayerFeature"]
```

- [ ] **Step 7: Generate Alembic migration**

```bash
cd apps/api
DATABASE_URL=postgresql://history:history@localhost:5432/history alembic revision --autogenerate -m "initial schema"
```

Expected: creates file `alembic/versions/xxxx_initial_schema.py`

Rename it: `alembic/versions/0001_initial_schema.py` and update `revision` identifier to `0001`.

- [ ] **Step 8: Review generated migration**

Open the generated file. Verify it contains:
- `CREATE TABLE entities`
- `CREATE TABLE entity_names`
- `CREATE TABLE territories` with geometry columns
- `CREATE TABLE events`
- `CREATE TABLE event_entities`
- `CREATE TABLE layers`
- `CREATE TABLE layer_features`

Manually add spatial indexes if autogenerate missed them. After `op.create_table('territories', ...)` add:

```python
op.execute("CREATE INDEX idx_territories_geom ON territories USING GIST(geom)")
op.execute("CREATE INDEX idx_territories_simplified ON territories USING GIST(simplified_geom)")
op.execute("CREATE INDEX idx_territories_years ON territories(year_start, year_end)")
op.execute("CREATE INDEX idx_territories_entity_years ON territories(entity_id, year_start, year_end)")
op.execute("CREATE INDEX idx_entity_names_years ON entity_names(year_start, year_end)")
op.execute("CREATE INDEX idx_events_years ON events(year_start, year_end)")
```

In `downgrade()` add corresponding `op.drop_index` calls for each.

- [ ] **Step 9: Run migration**

```bash
make migrate
# or directly:
DATABASE_URL=postgresql://history:history@localhost:5432/history alembic upgrade head
```

Expected: `Running upgrade -> 0001, initial schema`

- [ ] **Step 10: Run model tests — confirm they pass**

```bash
cd apps/api && pytest tests/test_models.py -v
```

Expected: all 3 PASS.

- [ ] **Step 11: Commit**

```bash
git add apps/api/app/models/ apps/api/alembic/
git commit -m "feat: orm models + initial postgis schema migration"
```

---

## Task 5: Year Utility + BCE/CE Handling

**Files:**
- Create: `apps/api/app/utils/year.py`
- Create: `apps/api/tests/test_year_utils.py`

- [ ] **Step 1: Write failing tests**

Create `apps/api/tests/test_year_utils.py`:

```python
import pytest
from app.utils.year import year_to_display, display_to_year, normalize_year, snap_to_snapshot


def test_year_to_display_bce():
    assert year_to_display(-264) == "264 BCE"


def test_year_to_display_ce():
    assert year_to_display(117) == "117 CE"


def test_year_to_display_one_bce():
    assert year_to_display(-1) == "1 BCE"


def test_year_to_display_one_ce():
    assert year_to_display(1) == "1 CE"


def test_no_year_zero():
    with pytest.raises(ValueError, match="Year 0 does not exist"):
        year_to_display(0)


def test_display_to_year_bce():
    assert display_to_year("264 BCE") == -264


def test_display_to_year_ce():
    assert display_to_year("117 CE") == 117


def test_display_to_year_case_insensitive():
    assert display_to_year("264 bce") == -264


def test_snap_to_snapshot_exact():
    snapshots = list(range(-500, 501, 25))
    assert snap_to_snapshot(-264, snapshots) == -275


def test_snap_to_snapshot_above():
    snapshots = list(range(-500, 501, 25))
    assert snap_to_snapshot(-251, snapshots) == -250


def test_snap_to_snapshot_exact_match():
    snapshots = list(range(-500, 501, 25))
    assert snap_to_snapshot(-500, snapshots) == -500
```

Run: `pytest tests/test_year_utils.py -v`
Expected: all FAIL with `ImportError`.

- [ ] **Step 2: Implement year.py**

Create `apps/api/app/utils/year.py`:

```python
import bisect
import re


def year_to_display(year: int) -> str:
    if year == 0:
        raise ValueError("Year 0 does not exist in historical convention")
    if year < 0:
        return f"{abs(year)} BCE"
    return f"{year} CE"


def display_to_year(s: str) -> int:
    s = s.strip().upper()
    match = re.fullmatch(r"(\d+)\s*(BCE|BC|CE|AD)", s)
    if not match:
        raise ValueError(f"Cannot parse year string: {s!r}")
    n = int(match.group(1))
    era = match.group(2)
    if era in ("BCE", "BC"):
        return -n
    return n


def normalize_year(year: int) -> int:
    """Validate year is non-zero integer."""
    if year == 0:
        raise ValueError("Year 0 does not exist")
    return year


def snap_to_snapshot(year: int, snapshots: list[int]) -> int:
    """Return nearest snapshot year (rounds toward lower/equal)."""
    sorted_snaps = sorted(snapshots)
    idx = bisect.bisect_right(sorted_snaps, year) - 1
    idx = max(0, min(idx, len(sorted_snaps) - 1))
    return sorted_snaps[idx]
```

- [ ] **Step 3: Run tests**

```bash
cd apps/api && pytest tests/test_year_utils.py -v
```

Expected: all PASS.

- [ ] **Step 4: Commit**

```bash
git add apps/api/app/utils/ apps/api/tests/test_year_utils.py
git commit -m "feat: bce/ce year utilities with zero-exclusion guard"
```

---

## Task 6: Redis Cache Service

**Files:**
- Create: `apps/api/app/cache.py`
- Create: `apps/api/app/services/cache_service.py`
- Create: `apps/api/tests/test_cache_service.py`

- [ ] **Step 1: Write failing tests**

Create `apps/api/tests/test_cache_service.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch

from app.services.cache_service import make_world_state_key, CacheService


def test_cache_key_format():
    key = make_world_state_key(year=-264, layer="political", zoom=4, tile_x=8, tile_y=3)
    assert key == "worldstate:-264:political:4:8:3"


def test_cache_key_positive_year():
    key = make_world_state_key(year=117, layer="political", zoom=5, tile_x=1, tile_y=2)
    assert key == "worldstate:117:political:5:1:2"


async def test_cache_miss_returns_none():
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    svc = CacheService(redis=mock_redis)
    result = await svc.get_world_state(-264, "political", 4, 8, 3)
    assert result is None


async def test_cache_hit_returns_data():
    mock_redis = AsyncMock()
    mock_redis.get.return_value = b'{"type":"FeatureCollection","features":[]}'
    svc = CacheService(redis=mock_redis)
    result = await svc.get_world_state(-264, "political", 4, 8, 3)
    assert result == {"type": "FeatureCollection", "features": []}


async def test_cache_set_calls_redis():
    mock_redis = AsyncMock()
    svc = CacheService(redis=mock_redis)
    data = {"type": "FeatureCollection", "features": []}
    await svc.set_world_state(-264, "political", 4, 8, 3, data)
    mock_redis.set.assert_called_once()
    call_args = mock_redis.set.call_args
    assert call_args[0][0] == "worldstate:-264:political:4:8:3"
```

Run: `pytest tests/test_cache_service.py -v`
Expected: all FAIL with `ImportError`.

- [ ] **Step 2: Create cache.py (Redis client)**

Create `apps/api/app/cache.py`:

```python
import redis.asyncio as aioredis
from app.config import settings

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=False)
    return _redis
```

- [ ] **Step 3: Create cache_service.py**

Create `apps/api/app/services/__init__.py` (empty).

Create `apps/api/app/services/cache_service.py`:

```python
import json
from typing import Any

import redis.asyncio as aioredis

CACHE_TTL = 86400  # 24 hours — historical data is immutable


def make_world_state_key(year: int, layer: str, zoom: int, tile_x: int, tile_y: int) -> str:
    return f"worldstate:{year}:{layer}:{zoom}:{tile_x}:{tile_y}"


class CacheService:
    def __init__(self, redis: aioredis.Redis):
        self.redis = redis

    async def get_world_state(
        self, year: int, layer: str, zoom: int, tile_x: int, tile_y: int
    ) -> dict | None:
        key = make_world_state_key(year, layer, zoom, tile_x, tile_y)
        raw = await self.redis.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    async def set_world_state(
        self, year: int, layer: str, zoom: int, tile_x: int, tile_y: int, data: dict
    ) -> None:
        key = make_world_state_key(year, layer, zoom, tile_x, tile_y)
        await self.redis.set(key, json.dumps(data), ex=CACHE_TTL)
```

- [ ] **Step 4: Run tests**

```bash
cd apps/api && pytest tests/test_cache_service.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add apps/api/app/cache.py apps/api/app/services/ apps/api/tests/test_cache_service.py
git commit -m "feat: redis cache service with worldstate key scheme"
```

---

## Task 7: World State Service + Query

**Files:**
- Create: `apps/api/app/schemas/world.py`
- Create: `apps/api/app/services/world_state.py`
- Create: `apps/api/tests/test_world_state.py`
- Modify: `apps/api/app/routers/world.py`

- [ ] **Step 1: Write failing tests**

Create `apps/api/tests/test_world_state.py`:

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


async def test_world_state_empty_db_returns_feature_collection():
    """With empty DB, should return valid empty FeatureCollection."""
    from app.services.world_state import WorldStateService

    mock_db = AsyncMock()
    mock_db.execute.return_value = MagicMock(mappings=lambda: MagicMock(all=lambda: []))

    svc = WorldStateService(db=mock_db)
    result = await svc.get_state(
        year=-264, bbox=(-180, -90, 180, 90), zoom=4, layer="political"
    )
    assert result["type"] == "FeatureCollection"
    assert result["year"] == -264
    assert isinstance(result["features"], list)


async def test_world_state_year_passed_to_query():
    from app.services.world_state import WorldStateService

    mock_db = AsyncMock()
    execute_mock = AsyncMock()
    execute_mock.mappings.return_value.all.return_value = []
    mock_db.execute.return_value = execute_mock

    svc = WorldStateService(db=mock_db)
    await svc.get_state(year=-500, bbox=(-180, -90, 180, 90), zoom=4, layer="political")

    call_args = mock_db.execute.call_args
    # year parameter must be present in query bindings
    params = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get("params", {})
    assert params.get("year") == -500
```

Run: `pytest tests/test_world_state.py -v`
Expected: all FAIL with `ImportError`.

- [ ] **Step 2: Create world state schema**

Create `apps/api/app/schemas/__init__.py` (empty).

Create `apps/api/app/schemas/world.py`:

```python
from typing import Any
from pydantic import BaseModel


class WorldStateResponse(BaseModel):
    type: str = "FeatureCollection"
    year: int
    snapshot_year: int
    features: list[dict[str, Any]]
```

- [ ] **Step 3: Create world_state.py service**

Create `apps/api/app/services/world_state.py`:

```python
import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

SNAPSHOT_YEARS = list(range(-500, 501, 25))
SNAPSHOT_YEARS = [y for y in SNAPSHOT_YEARS if y != 0]  # exclude year 0

WORLD_STATE_SQL = text("""
    SELECT
        e.id::text        AS entity_id,
        e.slug            AS slug,
        e.type            AS type,
        e.color           AS color,
        en.name           AS name,
        t.confidence      AS confidence,
        ST_AsGeoJSON(
            CASE WHEN :zoom < 7 THEN t.simplified_geom ELSE t.geom END
        )::json           AS geometry
    FROM territories t
    JOIN entities e ON t.entity_id = e.id
    JOIN entity_names en
        ON en.entity_id = e.id
        AND en.year_start <= :year
        AND (en.year_end IS NULL OR en.year_end > :year)
        AND en.is_primary = true
    WHERE
        t.year_start <= :year
        AND (t.year_end IS NULL OR t.year_end > :year)
        AND t.geom && ST_MakeEnvelope(:min_x, :min_y, :max_x, :max_y, 4326)
    ORDER BY e.slug
""")


def _snap_year(year: int) -> int:
    from app.utils.year import snap_to_snapshot
    return snap_to_snapshot(year, SNAPSHOT_YEARS)


class WorldStateService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_state(
        self,
        year: int,
        bbox: tuple[float, float, float, float],
        zoom: int,
        layer: str = "political",
    ) -> dict[str, Any]:
        min_x, min_y, max_x, max_y = bbox
        rows = await self.db.execute(
            WORLD_STATE_SQL,
            params={
                "year": year,
                "zoom": zoom,
                "min_x": min_x,
                "min_y": min_y,
                "max_x": max_x,
                "max_y": max_y,
            },
        )
        features = []
        for row in rows.mappings().all():
            features.append({
                "type": "Feature",
                "id": row["slug"],
                "geometry": row["geometry"],
                "properties": {
                    "entity_id": row["entity_id"],
                    "slug": row["slug"],
                    "name": row["name"],
                    "type": row["type"],
                    "color": row["color"],
                    "confidence": row["confidence"],
                },
            })

        return {
            "type": "FeatureCollection",
            "year": year,
            "snapshot_year": _snap_year(year),
            "features": features,
        }
```

- [ ] **Step 4: Wire router to service**

Replace `apps/api/app/routers/world.py`:

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import get_redis
from app.database import get_db
from app.services.cache_service import CacheService
from app.services.world_state import WorldStateService, SNAPSHOT_YEARS
from app.utils.year import normalize_year

router = APIRouter()


@router.get("/state")
async def get_world_state(
    year: int = Query(..., description="Year as integer. Negative = BCE."),
    min_x: float = Query(-180.0),
    min_y: float = Query(-90.0),
    max_x: float = Query(180.0),
    max_y: float = Query(90.0),
    zoom: int = Query(4, ge=1, le=20),
    layer: str = Query("political"),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    normalize_year(year)  # raises 422 if year == 0

    cache = CacheService(redis=redis)
    # Use integer tile proxy: quantize bbox to 10-degree grid for cache key
    tx = int(min_x // 10)
    ty = int(min_y // 10)
    cached = await cache.get_world_state(year, layer, zoom, tx, ty)
    if cached:
        return cached

    svc = WorldStateService(db=db)
    result = await svc.get_state(year=year, bbox=(min_x, min_y, max_x, max_y), zoom=zoom, layer=layer)

    await cache.set_world_state(year, layer, zoom, tx, ty, result)
    return result


@router.get("/snapshots")
async def get_snapshots():
    return {"snapshots": SNAPSHOT_YEARS}
```

- [ ] **Step 5: Run tests**

```bash
cd apps/api && pytest tests/test_world_state.py -v
```

Expected: all PASS.

- [ ] **Step 6: Integration test the endpoint (requires running DB)**

```bash
# With docker stack running:
curl "http://localhost:8000/api/v1/world/state?year=-264&zoom=4"
```

Expected: `{"type":"FeatureCollection","year":-264,"snapshot_year":-275,"features":[]}`

- [ ] **Step 7: Commit**

```bash
git add apps/api/app/schemas/ apps/api/app/services/world_state.py apps/api/app/routers/world.py apps/api/tests/test_world_state.py
git commit -m "feat: world state service + cached /world/state endpoint"
```

---

## Task 8: Data Ingestion Pipeline

**Files:**
- Create: `packages/data/__init__.py`
- Create: `packages/data/normalize.py`
- Create: `packages/data/entity_map.py`
- Create: `packages/data/sources/base.py`
- Create: `packages/data/sources/manual.py`
- Create: `packages/data/ingest.py`
- Create: `packages/data/tests/conftest.py`
- Create: `packages/data/tests/test_normalize.py`

- [ ] **Step 1: Write normalize tests**

Create `packages/data/tests/test_normalize.py`:

```python
from shapely.geometry import shape, mapping
import pytest
from data.normalize import to_multipolygon, validate_geometry, simplify_geometry


def test_polygon_becomes_multipolygon():
    polygon = {"type": "Polygon", "coordinates": [[[0,0],[1,0],[1,1],[0,1],[0,0]]]}
    result = to_multipolygon(polygon)
    assert result["type"] == "MultiPolygon"


def test_multipolygon_unchanged():
    mp = {"type": "MultiPolygon", "coordinates": [[[[0,0],[1,0],[1,1],[0,1],[0,0]]]]}
    result = to_multipolygon(mp)
    assert result["type"] == "MultiPolygon"


def test_invalid_geometry_raises():
    # self-intersecting polygon
    bad = {"type": "Polygon", "coordinates": [[[0,0],[1,1],[1,0],[0,1],[0,0]]]}
    with pytest.raises(ValueError, match="Invalid geometry"):
        validate_geometry(bad)


def test_simplify_returns_multipolygon():
    mp = {"type": "MultiPolygon", "coordinates": [[[[0,0],[1,0],[1,1],[0,1],[0,0]]]]}
    result = simplify_geometry(mp, tolerance=0.01)
    assert result["type"] == "MultiPolygon"
```

Run: `pytest packages/data/tests/test_normalize.py -v`
Expected: all FAIL.

- [ ] **Step 2: Create normalize.py**

Create `packages/data/normalize.py`:

```python
from typing import Any

from shapely.geometry import mapping, shape
from shapely.validation import make_valid


def to_multipolygon(geojson: dict) -> dict:
    """Convert Polygon → MultiPolygon. Pass through MultiPolygon."""
    geom = shape(geojson)
    if geom.geom_type == "Polygon":
        from shapely.geometry import MultiPolygon
        geom = MultiPolygon([geom])
    elif geom.geom_type != "MultiPolygon":
        raise ValueError(f"Expected Polygon or MultiPolygon, got {geom.geom_type}")
    return mapping(geom)


def validate_geometry(geojson: dict) -> dict:
    """Validate geometry is valid. Raise ValueError if not."""
    geom = shape(geojson)
    if not geom.is_valid:
        raise ValueError(f"Invalid geometry: {geom.is_valid_reason}")
    return geojson


def fix_geometry(geojson: dict) -> dict:
    """Attempt repair of invalid geometry. Returns MultiPolygon."""
    geom = make_valid(shape(geojson))
    return to_multipolygon(mapping(geom))


def simplify_geometry(geojson: dict, tolerance: float = 0.1) -> dict:
    """Simplify geometry for low-zoom rendering."""
    geom = shape(geojson).simplify(tolerance, preserve_topology=True)
    return to_multipolygon(mapping(geom))
```

- [ ] **Step 3: Run normalize tests**

```bash
cd packages/data && pytest tests/test_normalize.py -v
```

Expected: all PASS.

- [ ] **Step 4: Create entity_map.py**

Create `packages/data/entity_map.py`:

```python
# Maps source feature names → canonical entity slugs.
# Explicit > fuzzy matching. Add entries as new sources are ingested.

ENTITY_SLUG_MAP: dict[str, str] = {
    # Roman civilization variants
    "Roman Empire": "roman-empire",
    "Roman Republic": "roman-empire",
    "Roma": "roman-empire",
    "ROMAN_EMP": "roman-empire",
    "Rome": "roman-empire",

    # Han China variants
    "Han Dynasty": "han-dynasty",
    "Han China": "han-dynasty",
    "HAN": "han-dynasty",
    "Han": "han-dynasty",
}


def resolve_slug(source_name: str) -> str | None:
    """Return canonical entity slug for source_name, or None if unmapped."""
    return ENTITY_SLUG_MAP.get(source_name)
```

- [ ] **Step 5: Create source base class**

Create `packages/data/sources/__init__.py` (empty).

Create `packages/data/sources/base.py`:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TerritoryRecord:
    entity_slug: str
    geojson: dict           # MultiPolygon GeoJSON geometry
    year_start: int
    year_end: int | None
    confidence: str = "approximate"
    source: str = "manual"


@dataclass
class EntityRecord:
    slug: str
    type: str
    color: str
    names: list[dict]       # [{name, language, year_start, year_end, is_primary}]


class SourceParser(ABC):
    @abstractmethod
    def get_entities(self) -> list[EntityRecord]:
        ...

    @abstractmethod
    def get_territories(self) -> list[TerritoryRecord]:
        ...
```

- [ ] **Step 6: Create manual source with Rome + Han seed data**

Create `packages/data/sources/manual.py`:

```python
"""
Hand-coded MVP seed data for Rome and Han Dynasty.
Geometries are simplified approximations for proof-of-concept only.
Real data should come from AWMC or Euratlas in future ingestion phases.
"""
from data.sources.base import EntityRecord, SourceParser, TerritoryRecord

ENTITIES = [
    EntityRecord(
        slug="roman-empire",
        type="empire",
        color="#C0392B",
        names=[
            {"name": "Roman Republic", "language": "en", "year_start": -509, "year_end": -27, "is_primary": True},
            {"name": "Roman Empire", "language": "en", "year_start": -27, "year_end": 476, "is_primary": True},
        ],
    ),
    EntityRecord(
        slug="han-dynasty",
        type="empire",
        color="#E67E22",
        names=[
            {"name": "Han Dynasty", "language": "en", "year_start": -206, "year_end": 220, "is_primary": True},
        ],
    ),
]

# Approximate bounding polygons. NOT historically precise.
# Replace with real GIS data from AWMC in Task 9+.
TERRITORIES = [
    # Roman Republic / Empire — Mediterranean basin approximation
    TerritoryRecord(
        entity_slug="roman-empire",
        geojson={
            "type": "MultiPolygon",
            "coordinates": [[[
                [-10.0, 30.0], [40.0, 30.0], [45.0, 42.0],
                [35.0, 47.0], [15.0, 50.0], [-5.0, 44.0],
                [-10.0, 36.0], [-10.0, 30.0]
            ]]]
        },
        year_start=-264,
        year_end=476,
        confidence="approximate",
        source="manual-mvp",
    ),
    # Han Dynasty — East Asia approximation
    TerritoryRecord(
        entity_slug="han-dynasty",
        geojson={
            "type": "MultiPolygon",
            "coordinates": [[[
                [100.0, 20.0], [135.0, 20.0], [135.0, 45.0],
                [120.0, 52.0], [100.0, 50.0], [95.0, 35.0],
                [100.0, 20.0]
            ]]]
        },
        year_start=-206,
        year_end=220,
        confidence="approximate",
        source="manual-mvp",
    ),
]


class ManualSource(SourceParser):
    def get_entities(self) -> list[EntityRecord]:
        return ENTITIES

    def get_territories(self) -> list[TerritoryRecord]:
        return TERRITORIES
```

- [ ] **Step 7: Create ingest.py**

Create `packages/data/ingest.py`:

```python
"""
Data ingestion CLI.
Usage: python -m data.ingest [--source manual] [--clear]
"""
import argparse
import asyncio
import json
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from data.normalize import fix_geometry, simplify_geometry, to_multipolygon
from data.sources.base import EntityRecord, TerritoryRecord
from data.sources.manual import ManualSource

import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+asyncpg://history:history@localhost:5432/history"
)


async def upsert_entity(session: AsyncSession, rec: EntityRecord) -> uuid.UUID:
    result = await session.execute(
        text("SELECT id FROM entities WHERE slug = :slug"), {"slug": rec.slug}
    )
    row = result.fetchone()
    if row:
        entity_id = row[0]
    else:
        entity_id = uuid.uuid4()
        await session.execute(
            text("INSERT INTO entities (id, slug, type, color) VALUES (:id, :slug, :type, :color)"),
            {"id": entity_id, "slug": rec.slug, "type": rec.type, "color": rec.color},
        )

    await session.execute(
        text("DELETE FROM entity_names WHERE entity_id = :eid"), {"eid": entity_id}
    )
    for name in rec.names:
        await session.execute(
            text("""
                INSERT INTO entity_names (id, entity_id, name, language, year_start, year_end, is_primary)
                VALUES (:id, :eid, :name, :lang, :ys, :ye, :primary)
            """),
            {
                "id": uuid.uuid4(), "eid": entity_id, "name": name["name"],
                "lang": name["language"], "ys": name["year_start"],
                "ye": name.get("year_end"), "primary": name["is_primary"],
            },
        )
    return entity_id


async def upsert_territory(
    session: AsyncSession, rec: TerritoryRecord, entity_id: uuid.UUID
) -> None:
    await session.execute(
        text("DELETE FROM territories WHERE entity_id = :eid AND year_start = :ys"),
        {"eid": entity_id, "ys": rec.year_start},
    )

    geom = to_multipolygon(rec.geojson)
    try:
        simplified = simplify_geometry(geom, tolerance=0.1)
    except Exception:
        simplified = geom

    geom_json = json.dumps(geom)
    simplified_json = json.dumps(simplified)

    await session.execute(
        text("""
            INSERT INTO territories
                (id, entity_id, geom, simplified_geom, year_start, year_end, confidence, source)
            VALUES
                (:id, :eid,
                 ST_SetSRID(ST_GeomFromGeoJSON(:geom), 4326),
                 ST_SetSRID(ST_GeomFromGeoJSON(:simplified), 4326),
                 :ys, :ye, :conf, :src)
        """),
        {
            "id": uuid.uuid4(), "eid": entity_id,
            "geom": geom_json, "simplified": simplified_json,
            "ys": rec.year_start, "ye": rec.year_end,
            "conf": rec.confidence, "src": rec.source,
        },
    )


async def run_ingest(source_name: str = "manual") -> None:
    engine = create_async_engine(DATABASE_URL, echo=False)
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    if source_name == "manual":
        source = ManualSource()
    else:
        raise ValueError(f"Unknown source: {source_name}")

    async with Session() as session:
        async with session.begin():
            for entity_rec in source.get_entities():
                print(f"  Upserting entity: {entity_rec.slug}")
                entity_id = await upsert_entity(session, entity_rec)

                for territory_rec in source.get_territories():
                    if territory_rec.entity_slug == entity_rec.slug:
                        print(f"    Upserting territory: {entity_rec.slug} {territory_rec.year_start}")
                        await upsert_territory(session, territory_rec, entity_id)

    print("Ingestion complete.")
    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="manual")
    args = parser.parse_args()
    asyncio.run(run_ingest(args.source))
```

- [ ] **Step 8: Create packages/data/__init__.py**

```python
```

(empty file)

- [ ] **Step 9: Run ingestion**

```bash
cd packages/data
DATABASE_URL=postgresql+asyncpg://history:history@localhost:5432/history python -m data.ingest --source manual
```

Expected output:
```
  Upserting entity: roman-empire
    Upserting territory: roman-empire -264
  Upserting entity: han-dynasty
    Upserting territory: han-dynasty -206
Ingestion complete.
```

- [ ] **Step 10: Verify data in DB**

```bash
docker compose -f infra/docker-compose.yml exec postgres \
  psql -U history -c "SELECT e.slug, en.name, t.year_start, t.year_end FROM territories t JOIN entities e ON e.id=t.entity_id JOIN entity_names en ON en.entity_id=e.id LIMIT 10;"
```

Expected: rows for roman-empire and han-dynasty.

- [ ] **Step 11: Verify world state endpoint returns data**

```bash
curl "http://localhost:8000/api/v1/world/state?year=-200&zoom=4" | python -m json.tool
```

Expected: FeatureCollection with 2 features (roman-empire, han-dynasty).

- [ ] **Step 12: Commit**

```bash
git add packages/data/ apps/api/tests/
git commit -m "feat: data ingestion pipeline with rome + han dynasty seed data"
```

---

## Task 9: Snapshot Precomputation + Layers Seed

**Files:**
- Create: `packages/data/snapshots.py`
- Modify: `packages/data/ingest.py` (add `--snapshots` flag)

- [ ] **Step 1: Create snapshots.py**

Create `packages/data/snapshots.py`:

```python
"""
Precompute world state snapshots for all classical era years.
Writes JSON files to data/snapshots/political/{year}.json
"""
import asyncio
import json
import os
from pathlib import Path

import httpx

SNAPSHOT_YEARS = [y for y in range(-500, 501, 25) if y != 0]
API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")
OUTPUT_DIR = Path(os.environ.get("SNAPSHOT_DIR", "../../data/snapshots/political"))


async def compute_snapshot(client: httpx.AsyncClient, year: int) -> dict:
    response = await client.get(
        f"{API_BASE}/api/v1/world/state",
        params={"year": year, "zoom": 4, "min_x": -180, "min_y": -90, "max_x": 180, "max_y": 90},
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()


async def run_snapshot_generation() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    async with httpx.AsyncClient() as client:
        for year in SNAPSHOT_YEARS:
            output_file = OUTPUT_DIR / f"{year}.json"
            if output_file.exists():
                print(f"  Skip {year} (exists)")
                continue
            print(f"  Computing snapshot for year {year}...")
            data = await compute_snapshot(client, year)
            output_file.write_text(json.dumps(data))
            print(f"  Saved {output_file}")

    print(f"Snapshots complete. {len(SNAPSHOT_YEARS)} years processed.")


if __name__ == "__main__":
    asyncio.run(run_snapshot_generation())
```

- [ ] **Step 2: Run snapshot precomputation**

```bash
# With API running:
cd packages/data
python -m data.snapshots
```

Expected: creates `data/snapshots/political/-500.json`, `-475.json`, ..., `500.json`.

- [ ] **Step 3: Seed layers table**

Add to `packages/data/ingest.py` (insert before `run_ingest` closes session):

```python
# Seed layer registry
layers = [
    ("political", "Political Borders", True),
    ("religious", "Religious Influence", False),
    ("trade_routes", "Trade Routes", False),
    ("military", "Military Campaigns", False),
    ("linguistic", "Linguistic Groups", False),
    ("migration", "Migration Patterns", False),
]
for layer_id, display_name, active in layers:
    await session.execute(
        text("""
            INSERT INTO layers (id, display_name, active)
            VALUES (:id, :name, :active)
            ON CONFLICT (id) DO UPDATE SET display_name = EXCLUDED.display_name
        """),
        {"id": layer_id, "name": display_name, "active": active},
    )
```

- [ ] **Step 4: Verify layers endpoint**

```bash
curl http://localhost:8000/api/v1/world/snapshots
```

Expected: `{"snapshots": [-500, -475, -450, ...]}`

- [ ] **Step 5: Commit**

```bash
git add packages/data/snapshots.py packages/data/ingest.py data/snapshots/
git commit -m "feat: snapshot precomputation + layer registry seed"
```

---

## Task 10: README + Environment Documentation

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create README.md**

Create `README.md`:

```markdown
# History Platform

Temporal world-state engine for interactive historical geography.

## Quick Start

### Prerequisites
- Docker + Docker Compose
- Python 3.12+
- Node.js 20+ (frontend, later)

### Setup

```bash
cp .env.example .env
make dev-build
# wait for stack to be healthy
make migrate
make seed
```

### Verify

```bash
curl http://localhost:8000/health
curl "http://localhost:8000/api/v1/world/state?year=-264&zoom=4"
```

## Year Convention

All years stored as integers. Negative = BCE. Year 0 does not exist.

- `-264` = 264 BCE
- `117` = 117 CE

## Development Commands

| Command | Effect |
|---------|--------|
| `make dev` | Start full Docker stack |
| `make stop` | Stop stack |
| `make migrate` | Run Alembic migrations |
| `make seed` | Ingest MVP civilization data |
| `make test` | Run all tests |

## Services

| Service | Port | Purpose |
|---------|------|---------|
| API | 8000 | FastAPI backend |
| PostgreSQL/PostGIS | 5432 | Spatial temporal DB |
| Redis | 6379 | World state cache |
| Neo4j | 7474/7687 | Entity relationship graph |
```

- [ ] **Step 2: Create .gitignore**

Create `.gitignore`:

```
.env
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
dist/
.ruff_cache/
data/raw/
node_modules/
.next/
```

- [ ] **Step 3: Final integration test**

```bash
make dev-build
make migrate
make seed

# Test world state returns data
curl "http://localhost:8000/api/v1/world/state?year=-100&zoom=4" | python -m json.tool

# Test year BCE display
curl "http://localhost:8000/api/v1/world/snapshots"

# Test cache (second request should be faster)
time curl "http://localhost:8000/api/v1/world/state?year=-100&zoom=4" > /dev/null
time curl "http://localhost:8000/api/v1/world/state?year=-100&zoom=4" > /dev/null
```

Expected: second request visibly faster (cache hit).

- [ ] **Step 4: Final commit**

```bash
git add README.md .gitignore
git commit -m "feat: complete milestone 0 - temporal backend foundation with rome + han data"
```

---

## Self-Review

### Spec Coverage Check

| Requirement | Covered By |
|-------------|-----------|
| Monorepo structure | Task 1 |
| Docker Compose (postgres, redis, neo4j, api) | Task 1 |
| PostGIS container | Task 1 |
| Redis container | Task 1 |
| FastAPI structure | Task 2 |
| Alembic setup | Task 3 |
| Entity tables | Task 4 |
| Temporal geometry tables | Task 4 |
| Event tables | Task 4 |
| Layer tables | Task 4, Task 9 |
| Shared UUID strategy | Task 4 (all PKs are UUID) |
| BCE/CE handling | Task 5 |
| Redis caching flow | Task 6 |
| World-state query | Task 7 |
| GeoJSON ingestion pipeline | Task 8 |
| Shapefile/GeoJSON parsing | Task 8 (normalize.py) |
| Python GIS libraries | Task 2 (pyproject.toml: Shapely, Fiona, GeoPandas) |
| API endpoint structure | Task 7 |
| Snapshot storage | Task 9 |
| Rome + Han data loading | Task 8 |
| Testing strategy | All tasks (TDD throughout) |
| Local dev workflow | Task 1 (Makefile) + Task 10 (README) |
| Environment variables | Task 1 (.env.example) |
| Temporal indexing | Task 4 (migration spatial+temporal indexes) |

### No Placeholders Found ✓
### Type Consistency Verified ✓
- `TerritoryRecord` defined in `base.py` Task 8, used in `manual.py` and `ingest.py` same task
- `WorldStateService.get_state()` signature consistent between service and router
- `make_world_state_key()` signature consistent between `cache_service.py` and tests
- Year integers used throughout — no mixing with display strings
