from __future__ import annotations

from app.api.v1.endpoints import admin_suite


def test_system_status_catalog_keeps_probe_contracts_separate_from_runtime_state():
    evidence = admin_suite._system_status_catalog()

    assert {item.key for item in evidence} >= {"api_liveness", "api_readiness", "startup", "release", "alembic", "event_bus", "workers", "voice"}
    assert all(item.runtime_status == "unchecked" for item in evidence)
    assert next(item for item in evidence if item.key == "api_readiness").source == "/ready"


def test_system_status_catalog_does_not_claim_live_success():
    serialized = " ".join(item.model_dump_json() for item in admin_suite._system_status_catalog())

    assert '"runtime_status":"ready"' not in serialized
    assert "Live-Probe" in serialized or "live" in serialized.lower()


def test_admin_suite_system_status_router_is_registered():
    from app.api.v1.api import api_router

    paths = {getattr(route, "path", "") for route in api_router.routes}

    assert "/admin-suite/system-status" in paths
