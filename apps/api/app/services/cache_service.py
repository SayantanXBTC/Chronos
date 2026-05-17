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
    ) -> dict[str, Any] | None:
        key = make_world_state_key(year, layer, zoom, tile_x, tile_y)
        raw = await self.redis.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    async def set_world_state(
        self,
        year: int,
        layer: str,
        zoom: int,
        tile_x: int,
        tile_y: int,
        data: dict[str, Any],
    ) -> None:
        key = make_world_state_key(year, layer, zoom, tile_x, tile_y)
        await self.redis.set(key, json.dumps(data), ex=CACHE_TTL)
