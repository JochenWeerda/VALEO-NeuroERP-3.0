from pathlib import Path


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
