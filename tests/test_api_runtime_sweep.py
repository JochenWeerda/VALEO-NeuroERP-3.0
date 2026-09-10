"""The live API gate must fail closed when its schema cannot be tested."""
import httpx
import pytest

from scripts.api_runtime_sweep import load_targets


@pytest.mark.parametrize("status,payload", [
    (404, {"detail": "Not Found"}),
    (200, {"detail": "Not Found"}),
    (200, {"openapi": "3.1.0", "paths": {}}),
])
def test_unusable_schema_is_not_success(status, payload):
    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(
        lambda request: httpx.Response(status, json=payload)
    )) as client:
        with pytest.raises((ValueError, httpx.HTTPStatusError)):
            load_targets(client, "/api/v1/openapi.json", set())


def test_reads_configured_schema_and_applies_skips():
    def respond(request):
        assert request.url.path == "/api/v1/openapi.json"
        return httpx.Response(200, json={"openapi": "3.1.0", "paths": {
            "/items": {"get": {}}, "/events": {"get": {}},
            "/items/{id}": {"get": {}},
        }})
    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(respond)) as client:
        assert load_targets(client, "/api/v1/openapi.json", {"/events"}) == ["/items"]
        with pytest.raises(ValueError):
            load_targets(client, "/api/v1/openapi.json", {"/events", "/items"})
