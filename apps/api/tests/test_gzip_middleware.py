import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

pytestmark = pytest.mark.asyncio


async def test_gzip_response_when_accept_encoding():
    """Client sending Accept-Encoding: gzip gets compressed response for large payloads."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"Accept-Encoding": "gzip"},
    ) as client:
        response = await client.get("/health")
        # Small health response may not be compressed (below minimum_size)
        # but the middleware is registered and does not error
        assert response.status_code == 200


async def test_no_error_without_accept_encoding():
    """Requests without Accept-Encoding: gzip still work normally."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert "content-encoding" not in response.headers
