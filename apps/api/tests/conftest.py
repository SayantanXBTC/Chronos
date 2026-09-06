from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.cache import get_redis
from app.database import get_db
from app.main import app


def _make_mock_db():
    """AsyncSession mock that returns empty results for any query."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result
    return mock_db


def _make_mock_redis():
    """Redis mock: cache always misses (get→None), set is a no-op."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    return mock_redis


@pytest.fixture
async def client():
    mock_db = _make_mock_db()
    mock_redis = _make_mock_redis()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_redis] = lambda: mock_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
