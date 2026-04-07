from app.integrations.services.superglue_onboarding_templates import (
    render_superglue_onboarding_env_template,
    render_superglue_onboarding_pack_json,
    render_superglue_onboarding_vault_template,
)


def test_superglue_onboarding_templates_render_from_pack(monkeypatch):
    monkeypatch.setattr(
        "app.integrations.services.superglue_onboarding_templates.build_superglue_onboarding_pack",
        lambda tenant_id: {
            "tenant_id": tenant_id,
            "environment": "staging",
            "vault_path_prefix": "valeo-neuroerp",
            "platform_secret_keys": {"AUTH_TOKEN": ["SUPERGLUE__TENANT__tenant-a__AUTH_TOKEN"]},
            "policy_keys": {"SUPERGLUE_RUN_RETENTION_DAYS": 30},
            "connectors": [
                {
                    "connector_key": "document_search",
                    "display_name": "Superglue Document Search",
                    "secret_keys": {
                        "SYSTEM_URL": ["SUPERGLUE__TENANT__tenant-a__CONNECTOR__document_search__SYSTEM_URL"],
                        "apiKey": ["SUPERGLUE__TENANT__tenant-a__CONNECTOR__document_search__APIKEY"],
                    },
                }
            ],
        },
    )

    json_text = render_superglue_onboarding_pack_json("tenant-a")
    env_text = render_superglue_onboarding_env_template("tenant-a")
    vault_text = render_superglue_onboarding_vault_template("tenant-a")

    assert '"tenant_id": "tenant-a"' in json_text
    assert "SUPERGLUE__TENANT__tenant-a__AUTH_TOKEN=" in env_text
    assert "SUPERGLUE_RUN_RETENTION_DAYS=30" in env_text
    assert "[connector:document_search]" in vault_text
    assert "apiKey=SUPERGLUE__TENANT__tenant-a__CONNECTOR__document_search__APIKEY" in vault_text
