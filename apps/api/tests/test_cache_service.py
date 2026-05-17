import json
import pytest
from unittest.mock import AsyncMock

from app.services.cache_service import CacheService, make_world_state_key

pytestmark = pytest.mark.asyncio


def test_cache_key_format():
    key = make_world_state_key(year=-264, layer="political", zoom=4, tile_x=8, tile_y=3)
    assert key == "worldstate:-264:political:4:8:3"


def test_cache_key_positive_year():
    key = make_world_state_key(year=117, layer="political", zoom=5, tile_x=1, tile_y=2)
    assert key == "worldstate:117:political:5:1:2"


def test_cache_key_negative_preserved():
    key = make_world_state_key(year=-500, layer="political", zoom=3, tile_x=0, tile_y=0)
    assert key == "worldstate:-500:political:3:0:0"


async def test_cache_miss_returns_none():
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    svc = CacheService(redis=mock_redis)
    result = await svc.get_world_state(-264, "political", 4, 8, 3)
    assert result is None


async def test_cache_hit_returns_parsed_dict():
    mock_redis = AsyncMock()
    mock_redis.get.return_value = '{"type":"FeatureCollection","features":[]}'  # str, not bytes
    svc = CacheService(redis=mock_redis)
    result = await svc.get_world_state(-264, "political", 4, 8, 3)
    assert result == {"type": "FeatureCollection", "features": []}


async def test_cache_corrupt_value_returns_none():
    mock_redis = AsyncMock()
    mock_redis.get.return_value = b"not valid json {"
    svc = CacheService(redis=mock_redis)
    result = await svc.get_world_state(-264, "political", 4, 8, 3)
    assert result is None


async def test_cache_set_uses_correct_key():
    mock_redis = AsyncMock()
    svc = CacheService(redis=mock_redis)
    data = {"type": "FeatureCollection", "features": []}
    await svc.set_world_state(-264, "political", 4, 8, 3, data)
    mock_redis.set.assert_called_once()
    call_args = mock_redis.set.call_args
    assert call_args[0][0] == "worldstate:-264:political:4:8:3"


async def test_cache_set_uses_ttl():
    mock_redis = AsyncMock()
    svc = CacheService(redis=mock_redis)
    data = {"type": "FeatureCollection", "features": []}
    await svc.set_world_state(-264, "political", 4, 8, 3, data)
    call_kwargs = mock_redis.set.call_args[1]
    assert "ex" in call_kwargs
    assert call_kwargs["ex"] == 86400


async def test_cache_set_serializes_to_json():
    mock_redis = AsyncMock()
    svc = CacheService(redis=mock_redis)
    data = {"type": "FeatureCollection", "features": [{"id": "rome"}]}
    await svc.set_world_state(-264, "political", 4, 8, 3, data)
    call_args = mock_redis.set.call_args
    stored_value = call_args[0][1]
    parsed = json.loads(stored_value)
    assert parsed == data
