from app.integrations.services.superglue_onboarding_pack import build_superglue_onboarding_pack


def test_superglue_onboarding_pack_builds_secret_key_candidates(monkeypatch):
    monkeypatch.setattr(
        "app.integrations.services.superglue_onboarding_pack.build_superglue_live_readiness",
        lambda tenant_id: {
            "provider_key": "superglue",
            "tenant_id": tenant_id,
            "environment": "staging",
            "connector_count": 1,
            "blocked_connector_count": 1,
            "recommended_actions": ["set live credentials"],
            "connectors": [
                {
                    "connector_key": "document_search",
                    "display_name": "Superglue Document Search",
                    "tool_id": "tenant-a.sg.document.search",
                    "ready": False,
                    "blockers": ["missing_credentials", "placeholder_system_url"],
                    "missing_credential_fields": ["apiKey", "accessToken"],
                }
            ],
        },
    )
    monkeypatch.setattr("app.integrations.services.superglue_onboarding_pack.settings.HASHICORP_VAULT_PATH_PREFIX", "valeo-neuroerp")

    pack = build_superglue_onboarding_pack("tenant-a")

    assert pack["tenant_id"] == "tenant-a"
    assert pack["blocked_connector_count"] == 1
    assert pack["platform_secret_keys"]["AUTH_TOKEN"][0].startswith("SUPERGLUE__TENANT__tenant-a")
    connector = pack["connectors"][0]
    assert "SYSTEM_URL" in connector["secret_keys"]
    assert "apiKey" in connector["secret_keys"]
    assert "accessToken" in connector["secret_keys"]
