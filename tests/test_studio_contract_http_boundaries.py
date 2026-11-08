"""HTTP authorization and PostgreSQL tenant boundaries for Studio contracts."""

from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.endpoints import closing_checklists, intrastat, portal_kundenwege
from app.auth.finance_roles import finance_read, finance_write
from app.auth.deps import get_current_user
from app.auth.portal_kunde import AUSWERTUNGEN, PortalKunde, portal_kunde
from app.core.database import engine, get_db
from app.core.screen_definitions_domain_batch15 import build_portal_zertifikate_screen_definition
from app.core.screen_definitions_kontrolle import BATCH8_KONTROLL_BUILDERS
from app.core.tenant import get_tenant_id


def _app(*routers):
    app = FastAPI()
    for router in routers:
        app.include_router(router, prefix="/api/v1")
    return app


@pytest.mark.integration
def test_intrastat_detail_http_uses_verified_tenant_and_hides_foreign_row(require_db):
    marker = uuid4().hex[:12]
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            with Session(bind=conn) as db:
                for tenant in ("a", "b"):
                    db.execute(text(
                        "INSERT INTO domain_compliance.intrastat_meldungen "
                        "(id, tenant_id, meldenummer, meldezeitraum, meldungsart, cn8_warennummer, "
                        "ursprungsland, bestimmungsland, statistischer_wert_eur, nettomasse_kg, "
                        "menge, mengeneinheit, geschaeftsvorgang_code, status) "
                        "VALUES (:id, :tenant, :number, '2026-10', 'EINGANG', '12345678', "
                        "'DE', 'FR', 100.5, 40, 2, 'ST', '11', 'ENTWURF')"
                    ), {"id": f"studio-http-{marker}-{tenant}",
                        "tenant": f"studio-http-{marker}-{tenant}",
                        "number": f"INT-HTTP-{marker}-{tenant}"})
                app = _app(intrastat.router)
                app.dependency_overrides[get_db] = lambda: db
                client = TestClient(app)
                assert client.get(f"/api/v1/intrastat/meldungen/studio-http-{marker}-a").status_code == 401
                app.dependency_overrides[get_tenant_id] = lambda: f"studio-http-{marker}-a"
                own = client.get(f"/api/v1/intrastat/meldungen/INT-HTTP-{marker}-a")
                assert own.status_code == 200
                assert own.json()["cn8_warennummer"] == "12345678"
                for identifier in (f"studio-http-{marker}-b", f"INT-HTTP-{marker}-b", "missing"):
                    assert client.get(f"/api/v1/intrastat/meldungen/{identifier}").status_code == 404
        finally:
            transaction.rollback()


@pytest.mark.integration
def test_closing_detail_http_requires_finance_role_and_verified_tenant(require_db):
    marker = uuid4().hex[:12]
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            with Session(bind=conn) as db:
                for tenant in ("a", "b"):
                    db.execute(text(
                        "INSERT INTO domain_erp.closing_checklists "
                        "(id, tenant_id, period, closing_type, status, items, period_start, period_end) "
                        "VALUES (:id, :tenant, '2026-10', 'monthly', 'draft', '[]'::jsonb, "
                        "'2026-10-01', '2026-10-31')"
                    ), {"id": f"studio-close-{marker}-{tenant}",
                        "tenant": f"studio-close-{marker}-{tenant}"})
                app = _app(closing_checklists.router)
                app.dependency_overrides[get_db] = lambda: db
                client = TestClient(app)
                own_path = f"/api/v1/closing-checklists/studio-close-{marker}-a"
                assert client.get(own_path).status_code == 401
                app.dependency_overrides[get_tenant_id] = lambda: f"studio-close-{marker}-a"
                app.dependency_overrides[get_current_user] = lambda: {"roles": ["SALES_LESEN"]}
                assert client.get(own_path).status_code == 403
                app.dependency_overrides[finance_read] = lambda: None
                own = client.get(own_path)
                assert own.status_code == 200
                assert own.json()["id"] == f"studio-close-{marker}-a"
                assert client.get(f"/api/v1/closing-checklists/studio-close-{marker}-b").status_code == 404
                assert client.get(f"/api/v1/closing-checklists/studio-close-{marker}-b?tenant_id=studio-close-{marker}-b").status_code == 404
                app.dependency_overrides[finance_write] = lambda: None
                mutation = client.post(
                    f"/api/v1/closing-checklists/studio-close-{marker}-b/items/GL-001/complete"
                    f"?tenant_id=studio-close-{marker}-b",
                    json={"item_code": "GL-001", "status": "completed", "completed_by": "attacker"},
                )
                assert mutation.status_code == 404
        finally:
            transaction.rollback()


def test_portal_certificate_list_uses_customer_permission_and_no_internal_inventory():
    definition = build_portal_zertifikate_screen_definition()
    assert definition["dataSources"][0]["endpoint"] == "/api/v1/portal/zertifikate"
    assert "/api/v1/portal/anfragen" not in str(definition)
    assert "/api/v1/zertifikate" not in str(definition)
    assert not definition.get("rowActions")
    app = _app(portal_kundenwege.router)
    app.dependency_overrides[get_db] = lambda: object()
    client = TestClient(app)
    assert client.get("/api/v1/portal/zertifikate").status_code == 401
    app.dependency_overrides[portal_kunde] = lambda: PortalKunde(
        "tenant-a", "customer-a", "user-a", False, rechte=frozenset()
    )
    assert client.get("/api/v1/portal/zertifikate").status_code == 403
    app.dependency_overrides[portal_kunde] = lambda: PortalKunde(
        "tenant-a", "customer-a", "user-a", False, rechte=frozenset({AUSWERTUNGEN})
    )
    assert client.get("/api/v1/portal/zertifikate").json() == []
    assert client.get("/api/v1/portal/zertifikate/customer-b").status_code == 404


def test_quality_worklist_uses_protocol_fields_from_quality_list_response():
    definition = BATCH8_KONTROLL_BUILDERS["annahme/qualitaets-check"]()
    assert "/api/v1/agrar/quality-protocols" in str(definition)
    assert {"protocol_number", "is_final", "moisture_pct"} <= {
        column["key"] for table in definition["tables"] for column in table["columns"]
    }
