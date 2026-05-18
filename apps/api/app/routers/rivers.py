import json

from fastapi import APIRouter, Depends

from app.cache import get_redis
from app.database import get_db
from app.services.rivers_service import RiversService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

_RIVERS_CACHE_KEY = "rivers:all"
_RIVERS_TTL = 86400 * 7  # 7 days — rivers don't change


@router.get("")
async def get_rivers(
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    raw = await redis.get(_RIVERS_CACHE_KEY)
    if raw is not None:
        try:
            return json.loads(raw)
        except Exception:
            pass

    svc = RiversService(db=db)
    result = await svc.get_rivers()
    await redis.set(_RIVERS_CACHE_KEY, json.dumps(result), ex=_RIVERS_TTL)
    return result
