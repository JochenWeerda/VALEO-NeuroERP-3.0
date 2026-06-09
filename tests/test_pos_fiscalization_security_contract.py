from pathlib import Path

import pytest

from app.services.fiscalization.service import FiscalizationService


def test_frontend_contains_no_fiscal_provider_secrets():
    source = Path("packages/frontend-web/src/lib/services/fiskaly-tse.ts").read_text(encoding="utf-8")

    assert "VITE_FISKALY_API_KEY" not in source
    assert "VITE_FISKALY_API_SECRET" not in source
    assert "api_secret" not in source
    assert "/api/v1/pos/fiscalization/" in source


def test_legacy_dsfinvk_endpoint_contains_no_fixed_receipts():
    source = Path("app/api/v1/endpoints/pos_dsfinvk.py").read_text(encoding="utf-8")

    assert "BON-20260324" not in source
    assert "_build_transactions" not in source
    assert "FiscalizationService" in source


def test_tenant_settings_reject_and_redact_secret_keys():
    settings = {
        "terminal_id": "POS-1",
        "nested": {"api_token": "must-not-be-stored"},
        "api_secret": "must-not-be-returned",
    }

    assert FiscalizationService._secret_paths(settings) == [
        "settings.nested.api_token",
        "settings.api_secret",
    ]
    assert FiscalizationService._public_settings(settings) == {"terminal_id": "POS-1"}


def test_save_config_rejects_provider_secrets_before_database_write():
    class NoDatabaseAccess:
        def execute(self, *_args, **_kwargs):
            pytest.fail("database must not be touched for rejected secrets")

    service = FiscalizationService(NoDatabaseAccess(), "tenant-1")

    with pytest.raises(ValueError, match="Provider-Secrets"):
        service.save_config(
            provider="fiskaly",
            dsfinvk_provider="fiskaly",
            cash_register_id="TSS-1",
            client_id="CLIENT-1",
            simulation_allowed=False,
            settings={"terminal_id": "POS-1", "password": "forbidden"},
        )
