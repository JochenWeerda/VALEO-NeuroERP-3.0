from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.services import secrets_vault


@pytest.fixture(autouse=True)
def _reset_vault_cache():
    secrets_vault._VAULT_STORE.clear()
    secrets_vault._ACCESS_LOG.clear()
    yield
    secrets_vault._VAULT_STORE.clear()
    secrets_vault._ACCESS_LOG.clear()


def test_validate_startup_secrets_rejects_production_without_external_provider(monkeypatch):
    settings = SimpleNamespace(
        APP_ENV="production",
        API_DEV_TOKEN=None,
        SECRET_PROVIDER="env",
        REQUIRE_EXTERNAL_SECRETS_IN_PRODUCTION=True,
        SECRET_KEY=None,
        ENCRYPTION_KEY=None,
    )
    monkeypatch.setattr(secrets_vault, "_load_settings", lambda: settings)

    with pytest.raises(RuntimeError, match="externen Secret-Provider"):
        secrets_vault.validate_startup_secrets()


def test_validate_startup_secrets_rejects_dev_token_in_production(monkeypatch):
    settings = SimpleNamespace(
        APP_ENV="production",
        API_DEV_TOKEN="dev-token",
        SECRET_PROVIDER="hashicorp_vault",
        REQUIRE_EXTERNAL_SECRETS_IN_PRODUCTION=True,
        SECRET_KEY="set",
        ENCRYPTION_KEY="set",
    )
    monkeypatch.setattr(secrets_vault, "_load_settings", lambda: settings)

    with pytest.raises(RuntimeError, match="API_DEV_TOKEN"):
        secrets_vault.validate_startup_secrets()


def test_validate_startup_secrets_loads_required_keys_from_provider(monkeypatch):
    settings = SimpleNamespace(
        APP_ENV="production",
        API_DEV_TOKEN=None,
        SECRET_PROVIDER="hashicorp_vault",
        REQUIRE_EXTERNAL_SECRETS_IN_PRODUCTION=True,
        SECRET_KEY=None,
        ENCRYPTION_KEY=None,
    )
    monkeypatch.setattr(secrets_vault, "_load_settings", lambda: settings)
    monkeypatch.setattr(
        secrets_vault,
        "get_secret",
        lambda key, accessor="system": {"SECRET_KEY": "secret", "ENCRYPTION_KEY": "encrypt"}.get(key),
    )

    secrets_vault.validate_startup_secrets()

    assert settings.SECRET_KEY == "secret"
    assert settings.ENCRYPTION_KEY == "encrypt"
