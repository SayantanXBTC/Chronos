from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import get_redis
from app.database import get_db
from app.services.cache_service import CacheService
from app.services.world_state import SNAPSHOT_YEARS, WorldStateService
from app.utils.year import normalize_year

router = APIRouter()


@router.get("/state")
async def get_world_state(
    year: int = Query(..., description="Year as integer. Negative = BCE. Year 0 is invalid."),
    min_x: float = Query(-180.0, ge=-180.0, le=180.0),
    min_y: float = Query(-90.0, ge=-90.0, le=90.0),
    max_x: float = Query(180.0, ge=-180.0, le=180.0),
    max_y: float = Query(90.0, ge=-90.0, le=90.0),
    zoom: int = Query(4, ge=1, le=20),
    layer: str = Query("political"),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    try:
        normalize_year(year)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    cache = CacheService(redis=redis)
    tile_x = int(min_x // 10)
    tile_y = int(min_y // 10)

    cached = await cache.get_world_state(year, layer, zoom, tile_x, tile_y)
    if cached is not None:
        return cached

    svc = WorldStateService(db=db)
    result = await svc.get_state(
        year=year,
        bbox=(min_x, min_y, max_x, max_y),
        zoom=zoom,
        layer=layer,
    )

    await cache.set_world_state(year, layer, zoom, tile_x, tile_y, result)
    return result


@router.get("/snapshots")
async def get_snapshots():
    return {"snapshots": SNAPSHOT_YEARS}
