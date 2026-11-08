"""The remaining Studio detail routes require verified identity, not tenant headers."""

import inspect
import asyncio
from datetime import date
from uuid import uuid4

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.endpoints import (
    artikel_mengeneinheiten,
    individuelle_artikelnummern,
    kontrakt_mengenzeitraum,
    training,
    weighing_tickets,
)
from app.core.tenant import get_tenant_id
from app.core.database import engine


@pytest.mark.parametrize("router,path,endpoint", [
    (training.router, "/training/courses/course-id", training.get_course),
    (weighing_tickets.router, "/ticket-id", weighing_tickets.get_weighing_ticket),
    (kontrakt_mengenzeitraum.router, "/kontrakte/zuabschlagsgruppen/group-id", kontrakt_mengenzeitraum.get_zuabschlagsgruppe),
    (artikel_mengeneinheiten.router, "/artikel/mengeneinheiten/stamm/EH", artikel_mengeneinheiten.get_mengeneinheit),
    (individuelle_artikelnummern.router, "/artikel/individuelle-nummern/number-id", individuelle_artikelnummern.get_individuelle_nummer),
])
def test_detail_route_rejects_unverified_tenant_header(router, path, endpoint):
    tenant_dependency = inspect.signature(endpoint).parameters["tenant_id"].default.dependency
    assert tenant_dependency is get_tenant_id
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    route = next(r for r in app.routes if r.endpoint is endpoint)
    assert "GET" in route.methods and route.response_model is not None
    client = TestClient(app)
    assert client.get(f"/api/v1{path}", headers={"X-Tenant-ID": "other-tenant"}).status_code == 401


@pytest.mark.parametrize("router", [weighing_tickets.router, kontrakt_mengenzeitraum.router])
def test_all_weighing_and_contract_routes_use_verified_tenant(router):
    for route in router.routes:
        tenant_parameter = inspect.signature(route.endpoint).parameters.get("tenant_id")
        assert tenant_parameter is not None, route.path
        assert tenant_parameter.default.dependency is get_tenant_id, route.path


def test_contract_payload_identifiers_cannot_override_path():
    payload = kontrakt_mengenzeitraum.MengenzeitraumCreate(
        kontrakt_nr="other", zeitraum_von=date(2026, 10, 1),
        zeitraum_bis=date(2026, 10, 31), menge_t=1,
    )
    with pytest.raises(HTTPException) as exc:
        kontrakt_mengenzeitraum.create_mengenzeitraum("mine", payload, db=object(), tenant_id="tenant-a")
    assert exc.value.status_code == 422
    group_payload = kontrakt_mengenzeitraum.ZuAbschlagCreate(
        gruppe_id="other", bezeichnung="Test", betrag_eur=1,
    )
    with pytest.raises(HTTPException) as exc:
        kontrakt_mengenzeitraum.create_zuabschlag("mine", group_payload, db=object(), tenant_id="tenant-a")
    assert exc.value.status_code == 422


@pytest.mark.integration
def test_remaining_simple_details_use_postgres_tenant_rows(require_db):
    marker = uuid4().hex[:12]
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            with Session(bind=conn) as db:
                for suffix in ("a", "b"):
                    tenant = f"studio-rem-{marker}-{suffix}"
                    db.execute(text(
                        "INSERT INTO domain_shared.artikel_mengeneinheiten "
                        "(id, tenant_id, einheit_kuerzel, bezeichnung, dezimalstellen, aktiv) "
                        "VALUES (:id, :tenant, :unit, 'Studio Einheit', 3, true)"
                    ), {"id": f"unit-{marker}-{suffix}", "tenant": tenant,
                        "unit": f"U{marker[:6]}{suffix}"})
                    db.execute(text(
                        "INSERT INTO domain_shared.individuelle_artikelnummern "
                        "(id, tenant_id, artikel_nr, partner_nr, partner_typ, indiv_artikel_nr, aktiv) "
                        "VALUES (:id, :tenant, :article, 'P1', 'kunden', :number, true)"
                    ), {"id": f"indiv-{marker}-{suffix}", "tenant": tenant,
                        "article": f"ART-{marker}-{suffix}", "number": f"EXT-{marker}-{suffix}"})
                    db.execute(text(
                        "INSERT INTO domain_hr.training_courses "
                        "(id, tenant_id, course_code, title) VALUES (:id, :tenant, :code, 'Studio Schulung')"
                    ), {"id": f"course-{marker}-{suffix}", "tenant": tenant,
                        "code": f"C-{marker}-{suffix}"})
                    db.execute(text(
                        "INSERT INTO domain_shared.kontrakt_zuabschlagsgruppen "
                        "(id, tenant_id, gruppe_nr, bezeichnung, typ, aktiv) "
                        "VALUES (:id, :tenant, :number, 'Studio Zuschlag', 'zuschlag', true)"
                    ), {"id": f"group-{marker}-{suffix}", "tenant": tenant,
                        "number": f"G-{marker}-{suffix}"})
                tenant_a = f"studio-rem-{marker}-a"
                assert artikel_mengeneinheiten.get_mengeneinheit(f"U{marker[:6]}a", db=db, tenant_id=tenant_a).id == f"unit-{marker}-a"
                assert individuelle_artikelnummern.get_individuelle_nummer(f"indiv-{marker}-a", db=db, tenant_id=tenant_a).id == f"indiv-{marker}-a"
                assert asyncio.run(training.get_course(f"course-{marker}-a", db=db, tenant_id=tenant_a))["title"] == "Studio Schulung"
                assert kontrakt_mengenzeitraum.get_zuabschlagsgruppe(f"group-{marker}-a", db=db, tenant_id=tenant_a).id == f"group-{marker}-a"
                foreign_calls = (
                    lambda: artikel_mengeneinheiten.get_mengeneinheit(f"U{marker[:6]}b", db=db, tenant_id=tenant_a),
                    lambda: individuelle_artikelnummern.get_individuelle_nummer(f"indiv-{marker}-b", db=db, tenant_id=tenant_a),
                    lambda: asyncio.run(training.get_course(f"course-{marker}-b", db=db, tenant_id=tenant_a)),
                    lambda: kontrakt_mengenzeitraum.get_zuabschlagsgruppe(f"group-{marker}-b", db=db, tenant_id=tenant_a),
                )
                for read_foreign in foreign_calls:
                    with pytest.raises(HTTPException) as exc:
                        read_foreign()
                    assert exc.value.status_code == 404
        finally:
            transaction.rollback()
