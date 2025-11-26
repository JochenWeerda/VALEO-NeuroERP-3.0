import pytest
import httpx

from app.clients.base import BaseServiceClient, GatewayServiceError


class _DummyAsyncClient:
    def __init__(self, response: httpx.Response):
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def request(self, *args, **kwargs):
        return self._response


@pytest.mark.asyncio
async def test_base_client_normalizes_data(monkeypatch):
    response = httpx.Response(
        200,
        request=httpx.Request("GET", "http://service/api"),
        json={"data": {"items": [{"id": 1}], "meta": {"total": 1}}},
    )
    monkeypatch.setattr("app.clients.base.httpx.AsyncClient", lambda *a, **kw: _DummyAsyncClient(response))

    client = BaseServiceClient("http://service")
    data = await client._request("GET", "/api")
    assert data == {"items": [{"id": 1}], "meta": {"total": 1}}
    assert client._extract_items(data) == [{"id": 1}]


@pytest.mark.asyncio
async def test_base_client_wraps_errors(monkeypatch):
    error_response = httpx.Response(
        500,
        request=httpx.Request("GET", "http://service/api"),
        json={"detail": "boom"},
    )
    monkeypatch.setattr("app.clients.base.httpx.AsyncClient", lambda *a, **kw: _DummyAsyncClient(error_response))

    client = BaseServiceClient("http://service")
    with pytest.raises(GatewayServiceError) as exc:
        await client._request("GET", "/api")

    assert exc.value.status_code == 500
    assert exc.value.detail == "boom"

