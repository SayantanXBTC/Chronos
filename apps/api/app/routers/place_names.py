import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import get_redis
from app.database import get_db
from app.services.place_names_service import PlaceNamesService
from app.utils.year import normalize_year

router = APIRouter()


@router.get("")
async def get_place_names(
    year: int = Query(...),
    min_x: float = Query(-180.0, ge=-180.0, le=180.0),
    min_y: float = Query(-90.0, ge=-90.0, le=90.0),
    max_x: float = Query(180.0, ge=-180.0, le=180.0),
    max_y: float = Query(90.0, ge=-90.0, le=90.0),
    zoom: int = Query(4, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    try:
        normalize_year(year)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    tile_x = int(min_x // 10)
    tile_y = int(min_y // 10)
    cache_key = f"place_names:{year}:{zoom}:{tile_x}:{tile_y}"

    raw = await redis.get(cache_key)
    if raw is not None:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass  # treat corrupt cache entry as miss

    svc = PlaceNamesService(db=db)
    result = await svc.get_place_names(year=year, bbox=(min_x, min_y, max_x, max_y), zoom=zoom)

    await redis.set(cache_key, json.dumps(result), ex=86400)
    return result
