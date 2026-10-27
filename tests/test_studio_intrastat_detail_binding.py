"""Intrastat Studio detail reads the saved tenant-owned report, not validation output."""

import inspect
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.endpoints.intrastat import IntrastatMeldungOut, get_meldung, router
from app.core.database import engine
from app.core.screen_definitions_stamm_batch13 import build_artikel_zoll_intrastat
from app.core.tenant import get_tenant_id


@pytest.mark.integration
def test_intrastat_detail_is_tenant_scoped_and_typed(require_db):
    marker = uuid4().hex[:12]
    connection = engine.connect()
    transaction = connection.begin()
    try:
        with Session(bind=connection) as db:
            for tenant in ("tenant-a", "tenant-b"):
                db.execute(text(
                    "INSERT INTO domain_compliance.intrastat_meldungen "
                    "(id, tenant_id, meldenummer, meldezeitraum, meldungsart, cn8_warennummer, "
                    "ursprungsland, bestimmungsland, statistischer_wert_eur, nettomasse_kg, "
                    "menge, mengeneinheit, geschaeftsvorgang_code, status) "
                    "VALUES (:id, :tenant, :number, '2026-10', 'EINGANG', '12345678', 'DE', 'FR', "
                    "100.5, 40, 2, 'ST', '11', 'ENTWURF')"
                ), {"id": f"id-{marker}-{tenant}", "tenant": f"{marker}-{tenant}",
                    "number": f"INT-{marker}-{tenant}"})
            own = get_meldung(f"INT-{marker}-tenant-a", db=db, tenant_id=f"{marker}-tenant-a")
            assert own["id"] == f"id-{marker}-tenant-a"
            assert own["cn8_warennummer"] == "12345678"
            assert IntrastatMeldungOut.model_validate(own).meldenummer == f"INT-{marker}-tenant-a"
            for identifier in (f"id-{marker}-tenant-b", f"INT-{marker}-tenant-b", "missing"):
                with pytest.raises(HTTPException) as exc:
                    get_meldung(identifier, db=db, tenant_id=f"{marker}-tenant-a")
                assert exc.value.status_code == 404
    finally:
        transaction.rollback()
        connection.close()


def test_intrastat_studio_definition_uses_real_detail_contract():
    route = next(r for r in router.routes if r.path == "/intrastat/meldungen/{meldung_id}")
    assert "GET" in route.methods
    assert route.response_model is IntrastatMeldungOut
    assert inspect.signature(get_meldung).parameters["tenant_id"].default.dependency is get_tenant_id

    definition = build_artikel_zoll_intrastat()
    source = next(s for s in definition["dataSources"] if s["key"] == "entity")
    assert source["endpoint"] == "/api/v1/intrastat/meldungen/{entity_id}"
    fields = {field["key"] for field in definition["tabs"][0]["fields"]}
    assert {"meldenummer", "cn8_warennummer", "meldezeitraum", "nettomasse_kg"} <= fields
    assert "bezeichnung" not in fields
