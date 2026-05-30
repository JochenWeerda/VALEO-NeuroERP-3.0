from __future__ import annotations

from app.api.v1.endpoints import admin_suite


def test_compliance_catalog_keeps_runtime_and_external_evidence_separate():
    evidence = admin_suite._compliance_catalog()

    assert {item.key for item in evidence} >= {"gobd", "gdpr_art30", "gdpr_art33", "pos_tse", "elster", "atlas"}
    assert all(item.runtime_status == "unchecked" for item in evidence)
    assert all(item.external_gate in {"required", "not_required", "unchecked"} for item in evidence)
    assert next(item for item in evidence if item.key == "gobd").external_gate == "required"


def test_compliance_catalog_links_to_existing_domain_surfaces_without_claiming_live_success():
    evidence = admin_suite._compliance_catalog()
    serialized = " ".join(item.model_dump_json() for item in evidence)

    assert any(item.target_path == "/compliance/verarbeitungsverzeichnis" for item in evidence)
    assert any(item.target_path == "/compliance/datenpannen" for item in evidence)
    assert '"runtime_status":"ready"' not in serialized


def test_admin_suite_compliance_router_is_registered():
    from app.api.v1.api import api_router

    paths = {getattr(route, "path", "") for route in api_router.routes}

    assert "/admin-suite/compliance" in paths
