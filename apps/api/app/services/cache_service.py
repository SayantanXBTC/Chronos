import json
from typing import Any

import redis.asyncio as aioredis

CACHE_TTL = 86400  # 24 hours — historical data is immutable

WARM_YEARS = [y for y in list(range(-500, 501, 25)) + [1000, 1250, 1500, 1750, 2000] if y != 0]

FULL_WORLD_TILE = (-18, -9)


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
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None  # treat corrupt cache entry as miss

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

    async def is_world_state_cached(self, year: int, layer: str, zoom: int) -> bool:
        """Check if full-world snapshot is cached at given zoom."""
        tile_x, tile_y = FULL_WORLD_TILE
        key = make_world_state_key(year, layer, zoom, tile_x, tile_y)
        return await self.redis.exists(key) == 1
