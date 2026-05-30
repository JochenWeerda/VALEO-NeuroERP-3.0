from __future__ import annotations

from app.api.v1.endpoints import admin_suite


def test_connector_catalog_redacts_secrets_and_keeps_live_status_unchecked(monkeypatch):
    monkeypatch.setattr(
        admin_suite,
        "build_integration_bootstrap_summary",
        lambda: {
            "integrations": [
                {"integration_key": "oidc", "status": "ready", "missing": []},
                {"integration_key": "event_bus_nats", "status": "disabled", "missing": []},
                {"integration_key": "superglue", "status": "partial", "missing": ["SUPERGLUE_AUTH_TOKEN"]},
                {"integration_key": "voice", "status": "partial", "missing": ["OPENAI_API_KEY"]},
                {"integration_key": "crm_downstream", "status": "ready", "missing": []},
            ]
        },
    )
    connectors = admin_suite._connector_catalog()
    serialized = " ".join(item.model_dump_json() for item in connectors)

    assert all(item.live_status == "unchecked" for item in connectors)
    assert "Bearer " not in serialized
    assert "token-value" not in serialized
    assert next(item for item in connectors if item.key == "superglue").credential_status == "missing"


def test_device_catalog_never_treats_registration_as_live_uat():
    devices = admin_suite._device_catalog()

    assert any(item.key == "scale" for item in devices)
    assert all(item.live_status == "unchecked" for item in devices)


def test_operations_catalog_never_treats_deployable_restore_job_as_runtime_evidence():
    operations = admin_suite._operations_catalog()
    restore = next(item for item in operations if item.key == "restore_drill")

    assert restore.implementation_status == "available"
    assert restore.runtime_status == "unchecked"
