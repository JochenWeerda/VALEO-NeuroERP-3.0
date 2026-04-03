from app.integrations.services.superglue_secret_resolver import build_superglue_secret_keys, resolve_superglue_auth_token


def test_superglue_secret_keys_are_stable():
    keys = build_superglue_secret_keys("tenant-a")

    assert keys[0] == "SUPERGLUE__TENANT__tenant-a__AUTH_TOKEN"
    assert "SUPERGLUE__TENANT__TENANT_A__AUTH_TOKEN" in keys
    assert keys[-1] == "SUPERGLUE_AUTH_TOKEN"


def test_superglue_secret_resolver_prefers_tenant_specific_secret(monkeypatch):
    monkeypatch.setattr(
        "app.integrations.services.superglue_secret_resolver.get_first_secret",
        lambda keys, accessor="system": "tenant-token" if any("tenant-a" in key for key in keys) else None,
    )

    assert resolve_superglue_auth_token("tenant-a", allow_global_fallback=False) == "tenant-token"
