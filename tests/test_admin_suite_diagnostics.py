from __future__ import annotations

from app.api.v1.endpoints import admin_suite


def test_diagnostic_manifest_only_describes_redacted_not_collected_data():
    manifest = admin_suite._diagnostic_manifest()

    assert {item.key for item in manifest} >= {"release_metadata", "health_summary", "migration_summary", "connector_summary", "event_bus_summary", "worker_summary", "audit_summary"}
    assert all(item.collection_status == "not_collected" for item in manifest)
    assert all(item.redaction in {"required", "metadata_only"} for item in manifest)


def test_diagnostic_manifest_does_not_expose_secret_values_or_payloads():
    serialized = " ".join(item.model_dump_json() for item in admin_suite._diagnostic_manifest())

    assert "Bearer " not in serialized
    assert "token-value" not in serialized
    assert "password=" not in serialized
    assert "Event-Payloads" in serialized


def test_admin_suite_diagnostics_router_is_registered():
    from app.api.v1.api import api_router

    paths = {getattr(route, "path", "") for route in api_router.routes}

    assert "/admin-suite/diagnostics" in paths
