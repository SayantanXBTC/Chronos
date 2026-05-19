import asyncio
import logging
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.config import settings
from app.database import AsyncSessionLocal
from app.routers import admin, entities, events, place_names, rivers, sources, world
from app.services.cache_service import FULL_WORLD_TILE, WARM_YEARS, CacheService
from app.services.world_state import SNAPSHOT_YEARS, WorldStateService

logger = logging.getLogger(__name__)


async def _warm_cache_task() -> None:
    """Background task: pre-populate Redis for common snapshot years. Non-fatal."""
    await asyncio.sleep(2)  # let app fully start
    redis = None
    try:
        redis = aioredis.from_url(settings.redis_url, decode_responses=True)
        cache = CacheService(redis)

        async with AsyncSessionLocal() as db:
            svc = WorldStateService(db)
            warmed = 0
            for year in WARM_YEARS:
                if year not in SNAPSHOT_YEARS:
                    continue
                if await cache.is_world_state_cached(year, "political", 4):
                    continue
                result = await svc.get_state(year=year, bbox=(-180, -90, 180, 90), zoom=4)
                tile_x, tile_y = FULL_WORLD_TILE
                await cache.set_world_state(year, "political", 4, tile_x, tile_y, result)
                warmed += 1
            logger.info("[startup] Cache warmed: %d snapshots", warmed)
    except aioredis.exceptions.ConnectionError:
        logger.warning("[startup] Redis unavailable, skipping cache warm")
    except Exception:
        logger.exception("[startup] Cache warming failed (non-fatal)")
    finally:
        if redis is not None:
            await redis.aclose()


_background_tasks: set = set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    t = asyncio.create_task(_warm_cache_task())
    _background_tasks.add(t)
    t.add_done_callback(_background_tasks.discard)
    yield


app = FastAPI(
    title="History Platform API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(world.router, prefix="/api/v1/world", tags=["world"])
app.include_router(entities.router, prefix="/api/v1/entities", tags=["entities"])
app.include_router(events.router, prefix="/api/v1/events", tags=["events"])
app.include_router(place_names.router, prefix="/api/v1/place-names", tags=["place-names"])
app.include_router(rivers.router, prefix="/api/v1/rivers", tags=["rivers"])
app.include_router(sources.router, prefix="/api/v1/sources", tags=["sources"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.api_env}
