from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from app.services import secrets_vault


class _FakeResponse:
    def __init__(self, status: int, payload: dict | None = None):
        self.status = status
        self._payload = payload or {}

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


@pytest.fixture(autouse=True)
def _reset_vault_state(monkeypatch):
    secrets_vault._VAULT_STORE.clear()
    secrets_vault._ACCESS_LOG.clear()
    settings = SimpleNamespace(
        SECRET_PROVIDER="hashicorp_vault",
        APP_ENV="development",
        API_DEV_TOKEN=None,
        REQUIRE_EXTERNAL_SECRETS_IN_PRODUCTION=True,
        HASHICORP_VAULT_ADDR="https://vault.example.local",
        HASHICORP_VAULT_TOKEN="vault-token",
        HASHICORP_VAULT_MOUNT="secret",
        HASHICORP_VAULT_PATH_PREFIX="valeo",
        SECRET_KEY=None,
        ENCRYPTION_KEY=None,
    )
    monkeypatch.setattr(secrets_vault, "_load_settings", lambda: settings)
    yield
    secrets_vault._VAULT_STORE.clear()
    secrets_vault._ACCESS_LOG.clear()


def test_hashicorp_store_and_get_secret(monkeypatch):
    calls: list[tuple[str, str, dict | None]] = []

    def fake_urlopen(request, timeout=5):
        payload = None
        if request.data:
            payload = json.loads(request.data.decode("utf-8"))
        calls.append((request.method, request.full_url, payload))
        if request.method == "POST":
            return _FakeResponse(200, {"data": {"created": True}})
        return _FakeResponse(
            200,
            {
                "data": {
                    "data": {
                        "value": "vault-secret",
                        "metadata": {
                            "key": "SECRET_KEY",
                            "provider": "hashicorp_vault",
                            "secret_type": "api_key",
                        },
                    }
                }
            },
        )

    monkeypatch.setattr(secrets_vault, "urlopen", fake_urlopen)

    metadata = secrets_vault.store_secret(
        "SECRET_KEY",
        "vault-secret",
        provider=secrets_vault.SecretProvider.HASHICORP_VAULT,
    )
    value = secrets_vault.get_secret("SECRET_KEY", accessor="pytest")

    assert metadata.provider == secrets_vault.SecretProvider.HASHICORP_VAULT
    assert value == "vault-secret"
    assert calls[0][0] == "POST"
    assert calls[1][0] == "GET"
    assert calls[0][2]["data"]["value"] == "vault-secret"


def test_check_health_reports_external_vault_status(monkeypatch):
    def fake_request(method: str, url: str, payload=None):
        return 404, ""

    monkeypatch.setattr(secrets_vault, "_hashicorp_request", fake_request)

    health = secrets_vault.check_health()

    assert health["external_vault"]["configured_provider"] == "hashicorp_vault"
    assert health["external_vault"]["healthy"] is True
