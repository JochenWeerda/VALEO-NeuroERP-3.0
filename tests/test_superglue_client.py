import httpx
import pytest

from app.core.outbound_security import OutboundTargetPolicyError
from app.integrations.adapters.superglue.client import (
    SuperglueClient,
    SuperglueClientConfigError,
    SuperglueClientRequestError,
)
from app.integrations.services.integration_circuit_breaker import IntegrationCircuitBreaker


def test_superglue_client_requires_configured_url() -> None:
    client = SuperglueClient(base_url=None, rest_url=None, graphql_url=None)

    with pytest.raises(SuperglueClientConfigError):
        client.request("GET", "/tools")


def test_superglue_client_blocks_disallowed_targets() -> None:
    client = SuperglueClient(base_url="http://localhost:9999")

    with pytest.raises(OutboundTargetPolicyError):
        client.request("GET", "/tools")


def test_superglue_client_retries_and_sends_auth_header() -> None:
    attempts = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        assert request.headers["Authorization"] == "Bearer super-secret"
        if attempts["count"] == 1:
            return httpx.Response(503, json={"error": "temporary"})
        return httpx.Response(200, json={"ok": True})

    client = SuperglueClient(
        base_url="https://api.superglue.dev",
        auth_token="super-secret",
        retry_attempts=1,
        transport=httpx.MockTransport(handler),
    )

    result = client.request("GET", "/v1/tools")

    assert attempts["count"] == 2
    assert result == {"ok": True}


def test_superglue_client_uses_provider_specific_allowlist() -> None:
    client = SuperglueClient(
        base_url="https://sync.superglue.partner.example",
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json={"ok": True})),
    )

    assert client._resolve_target_url(mode="rest", path="/v1/sync") == "https://sync.superglue.partner.example/v1/sync"


def test_circuit_breaker_opens_after_repeated_failures() -> None:
    breaker = IntegrationCircuitBreaker(name="superglue-test", failure_threshold=2, recovery_timeout_seconds=60)
    client = SuperglueClient(
        base_url="https://api.superglue.dev",
        retry_attempts=0,
        breaker=breaker,
        transport=httpx.MockTransport(lambda request: httpx.Response(503, json={"error": "down"})),
    )

    with pytest.raises(SuperglueClientRequestError):
        client.request("GET", "/v1/tools")
    with pytest.raises(SuperglueClientRequestError):
        client.request("GET", "/v1/tools")

    assert breaker.state == "open"
