"""CommandEndpoint-Vertraege Batch2: Bonuslauf und Query-Import."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import l3_report_catalog, query_center
from app.core.database import get_db
from app.core.tenant import get_tenant_id


def _client_bonus():
    app = FastAPI()
    app.include_router(l3_report_catalog.router, prefix="/api/v1")
    db = Mock()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-a"
    return TestClient(app), db


def _client_query():
    app = FastAPI()
    app.include_router(query_center.router, prefix="/api/v1")
    db = Mock()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-a"
    return TestClient(app), db


def test_bonus_ce_dry_run_validates_without_create():
    http, db = _client_bonus()
    with patch(
        "app.services.l3_report_catalog_service.L3ReportCatalogService.validate_bonus_run_params"
    ) as validate, patch(
        "app.services.l3_report_catalog_service.L3ReportCatalogService.create_bonus_run"
    ) as create:
        response = http.post(
            "/api/v1/l3-report-catalog/bonus-runs/actions/calculate",
            json={
                "report_id": "bonus-by-customer",
                "from_date": "2026-01-01",
                "to_date": "2026-01-31",
                "rate_pct": "2.5",
                "reason": "Monatsbonus",
                "_mode": "dryRun",
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["mode"] == "dryRun"
    validate.assert_called_once()
    create.assert_not_called()
    db.commit.assert_not_called()


def test_bonus_ce_execute_creates_run():
    http, db = _client_bonus()
    with patch(
        "app.services.l3_report_catalog_service.L3ReportCatalogService.validate_bonus_run_params"
    ), patch(
        "app.services.l3_report_catalog_service.L3ReportCatalogService.create_bonus_run",
        return_value={
            "id": "run-1",
            "status": "calculated",
            "lines": 3,
            "total_basis": Decimal("100"),
            "total_bonus": Decimal("2.5"),
        },
    ) as create, patch(
        "app.services.mask_action_runtime_service._write_audit", return_value="a1"
    ), patch(
        "app.services.mask_action_runtime_service._write_outbox", return_value="o1"
    ):
        response = http.post(
            "/api/v1/l3-report-catalog/bonus-runs/actions/calculate",
            json={
                "report_id": "bonus-by-customer",
                "from_date": "2026-01-01",
                "to_date": "2026-01-31",
                "rate_pct": "2.5",
                "reason": "Monatsbonus",
            },
            headers={"X-User-ID": "agent-1"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["affectedIds"] == ["run-1"]
    create.assert_called_once()
    db.commit.assert_called()


def test_query_import_ce_dry_run_preview_only():
    http, db = _client_query()
    with patch(
        "app.api.v1.endpoints.query_center.service"
    ) as svc_factory:
        svc = Mock()
        svc.preview_import_signed.return_value = {
            "name": "Offene OP (Import)",
            "data_product_id": "ar_open",
            "selected_fields": ["id"],
            "would_import": True,
        }
        svc_factory.return_value = svc
        response = http.post(
            "/api/v1/query-center/actions/import",
            json={
                "bundle": {"schema_version": 1, "definition": {"name": "Offene OP"}, "signature": "x"},
                "reason": "Migration Test",
                "_mode": "dryRun",
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["mode"] == "dryRun"
    svc.preview_import_signed.assert_called_once()
    svc.import_signed.assert_not_called()
    db.commit.assert_not_called()


def test_query_import_ce_execute_saves():
    http, db = _client_query()
    with patch(
        "app.api.v1.endpoints.query_center.service"
    ) as svc_factory, patch(
        "app.services.mask_action_runtime_service._write_audit", return_value="a1"
    ), patch(
        "app.services.mask_action_runtime_service._write_outbox", return_value="o1"
    ):
        svc = Mock()
        svc.preview_import_signed.return_value = {
            "name": "Offene OP (Import)",
            "data_product_id": "ar_open",
            "selected_fields": ["id"],
            "would_import": True,
        }
        svc.import_signed.return_value = {"id": "def-9", "name": "Offene OP (Import)"}
        svc_factory.return_value = svc
        response = http.post(
            "/api/v1/query-center/actions/import",
            json={
                "bundle": {"schema_version": 1, "definition": {"name": "Offene OP"}, "signature": "x"},
                "reason": "Migration Test",
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["affectedIds"] == ["def-9"]
    svc.import_signed.assert_called_once()
    db.commit.assert_called()


def test_screen_definitions_batch2_command_endpoints():
    from app.core.screen_definitions import get_screen_definition

    bonus = get_screen_definition("auswertungen/bonus-berechnung")
    calc = next(a for a in bonus["actions"] if a["key"] == "calculate")
    assert calc["commandEndpoint"].endswith("/bonus-runs/actions/calculate")
    assert "inputFlow" not in calc

    abfrage = get_screen_definition("auswertungen/abfrage-center")
    imp = next(a for a in abfrage["actions"] if a["key"] == "import")
    assert imp["commandEndpoint"] == "/api/v1/query-center/actions/import"
    assert "inputFlow" not in imp


def test_bonus_ce_ignores_payload_tenant_override():
    """Masken-Payload-tenant_id wird gestrippt; Service bekommt Token-Tenant."""
    http, db = _client_bonus()
    with patch(
        "app.api.v1.endpoints.l3_report_catalog.L3ReportCatalogService"
    ) as Svc:
        inst = Mock()
        Svc.return_value = inst
        response = http.post(
            "/api/v1/l3-report-catalog/bonus-runs/actions/calculate",
            json={
                "report_id": "bonus-by-customer",
                "from_date": "2026-01-01",
                "to_date": "2026-01-31",
                "rate_pct": "2.5",
                "reason": "Monatsbonus",
                "tenant_id": "evil-tenant",
                "mandanten_id": "evil-tenant",
                "_mode": "dryRun",
            },
        )
    assert response.status_code == 200
    Svc.assert_called_once_with(db, "tenant-a")
    kwargs = inst.validate_bonus_run_params.call_args.kwargs
    assert "tenant_id" not in kwargs
    assert "mandanten_id" not in kwargs


def test_query_import_ce_ignores_payload_tenant_override():
    http, db = _client_query()
    with patch("app.api.v1.endpoints.query_center.service") as svc_factory:
        svc = Mock()
        svc.preview_import_signed.return_value = {
            "name": "OP (Import)",
            "data_product_id": "ar_open",
            "selected_fields": [],
            "would_import": True,
        }
        svc_factory.return_value = svc
        response = http.post(
            "/api/v1/query-center/actions/import",
            json={
                "bundle": {
                    "schema_version": 1,
                    "definition": {"name": "OP", "tenant_id": "evil"},
                    "signature": "x",
                },
                "reason": "Migration Test",
                "tenant_id": "evil-tenant",
                "mandanten_id": "evil-tenant",
                "_mode": "dryRun",
            },
        )
    assert response.status_code == 200
    svc_factory.assert_called_once_with(db, "tenant-a")
    svc.import_signed.assert_not_called()
