"""Auftragsbestaetigung als eigener DocFlow-Stand ``confirmed`` (BELEG-052, Nutzerentscheidung 09.11.2026).

Freigegeben (``open``) -> "Auftrag bestaetigen" -> ``confirmed``. Nur Verkaufsauftraege, nur aus ``open``,
Wiederholung mit demselben Schluessel ohne zweite Wirkung; danach bleiben Folgebelege und Storno moeglich.
"""
from __future__ import annotations

import importlib.util
import os
import uuid
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.orm import Session

pytestmark = pytest.mark.integration

WURZEL = Path(__file__).resolve().parents[1]
DB_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe")


def _migriere(verbindung, name: str) -> None:
    spec = importlib.util.spec_from_file_location(name, WURZEL / f"alembic/versions/{name}.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    with Operations.context(MigrationContext.configure(verbindung)):
        modul.upgrade()


@pytest.fixture
def w():
    try:
        engine = sa.create_engine(DB_URL, connect_args={"connect_timeout": 5, "application_name": "agent:claude"})
        verbindung = engine.connect()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    aussen = verbindung.begin()
    if not verbindung.execute(sa.text(
            "SELECT 1 FROM information_schema.columns WHERE table_schema = 'domain_docflow' "
            "AND table_name = 'document_headers' AND column_name = 'bausteine'")).scalar():
        _migriere(verbindung, "docflow_kopfbausteine_20261109")
    if "confirmed" not in (verbindung.execute(sa.text(
            "SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname = 'chk_docflow_header_status'")).scalar() or ""):
        _migriere(verbindung, "docflow_auftragsbestaetigung_20261109")
    sitzung = Session(bind=verbindung, join_transaction_mode="create_savepoint")
    mandant, kunde = f"ab-{uuid.uuid4().hex[:8]}", str(uuid.uuid4())
    sitzung.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true)"), {"t": mandant})
    from app.finance.steuerschluessel import richte_skr03_ein

    richte_skr03_ein(sitzung, mandant)
    sitzung.execute(sa.text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name) "
                            "VALUES (:id, :t, 'K-AB', 'Hof Bestaetigung')"), {"id": kunde, "t": mandant})
    sitzung.flush()
    try:
        yield {"db": sitzung, "mandant": mandant, "kunde": kunde}
    finally:
        sitzung.close()
        aussen.rollback()
        verbindung.close()


def _svc(w):
    from app.services.docflow_service import DocflowService

    return DocflowService(w["db"], w["mandant"], "verkauf-1")


def _beleg(w, art: str = "sales_order") -> str:
    from app.api.v1.schemas.docflow_schemas import DocflowCreateRequest, DocflowLineInput

    return _svc(w).create_document(DocflowCreateRequest.model_validate({
        "doc_type": art, "doc_number": f"E-{uuid.uuid4().hex[:6]}", "customer_id": w["kunde"],
        "items": [DocflowLineInput(article_number="W", quantity=10, unit="dt", unit_price=21.5, tax_code="3").model_dump()]}))


def _freigegeben(w, art: str = "sales_order") -> str:
    beleg = _beleg(w, art)
    _svc(w).release(beleg, f"rel-{uuid.uuid4().hex}", 1, None)
    return beleg


def _aktionen(w, beleg: str) -> dict:
    from app.services.docflow_belegadapter import lies_beleg

    return {a.key: a for a in lies_beleg(_svc(w), beleg).aktionen}


def test_freigegebener_auftrag_wird_bestaetigt_und_bleibt_umwandelbar(w):
    from app.core.exceptions import ValidationFailedError

    beleg = _freigegeben(w)
    assert "bestaetigen" in _aktionen(w, beleg)
    ergebnis = _svc(w).confirm(beleg, "ab-schluessel-1", 2)
    assert ergebnis["command"] == "confirm"
    kopf = _svc(w).fetch_header(beleg)
    assert (kopf["status"], int(kopf["version"])) == ("confirmed", 3)
    aktionen = _aktionen(w, beleg)
    assert "bestaetigen" not in aktionen
    assert aktionen["umwandeln:sales_delivery"].erlaubt and aktionen["stornieren"].erlaubt
    # Wiederholung mit demselben Schluessel: dieselbe Antwort, keine zweite Wirkung
    assert _svc(w).confirm(beleg, "ab-schluessel-1", 2)["idempotent_hit"] is True
    assert int(_svc(w).fetch_header(beleg)["version"]) == 3
    with pytest.raises(ValidationFailedError):
        _svc(w).confirm(beleg, "ab-schluessel-2", 3)  # schon bestaetigt
    historie = [h["to_status"] for h in _svc(w).fetch_status_history(beleg)]
    assert historie[-1] == "confirmed"


def test_entwurf_und_andere_belegarten_werden_nicht_bestaetigt(w):
    from app.core.exceptions import ValidationFailedError

    with pytest.raises(ValidationFailedError, match="freigegebener"):
        _svc(w).confirm(_beleg(w), "ab-entwurf", 1)
    with pytest.raises(ValidationFailedError, match="Verkaufsauftrag"):
        _svc(w).confirm(_freigegeben(w, "sales_offer"), "ab-angebot", 2)


def test_belegaktion_bestaetigen_ueber_die_maske(w):
    from app.services.docflow_belegaktionen import fuehre_aus, pruefe

    beleg = _freigegeben(w)
    nutzer = {"sub": "verkauf-1", "roles": ["SALES_BEARBEITEN"]}
    assert pruefe(w["db"], w["mandant"], "sales_order", beleg, "bestaetigen", nutzer, {}) == []
    satz = fuehre_aus(w["db"], w["mandant"], "sales_order", beleg, "bestaetigen", nutzer, {})
    assert "bestätigt" in satz
    assert _svc(w).fetch_header(beleg)["status"] == "confirmed"


def test_bestaetigter_auftrag_druckt_als_auftragsbestaetigung(w):
    from app.services.beleg_druck import belegtitel
    from app.services.docflow_belegadapter import lies_beleg

    beleg = _freigegeben(w)
    assert belegtitel(lies_beleg(_svc(w), beleg)) == "Auftrag"
    _svc(w).confirm(beleg, "ab-druck", 2)
    assert belegtitel(lies_beleg(_svc(w), beleg)) == "Auftragsbestätigung"


def test_rest_weg_bestaetigt_und_meldet_konflikt_und_unbekannt(w):
    """POST /docflow/{id}/confirm - derselbe Weg wie die Maske, mit Recht, Konflikt und unbekanntem Beleg."""
    import asyncio

    from fastapi import HTTPException

    from app.api.v1.endpoints.docflow import confirm_document
    from app.api.v1.schemas.docflow_schemas import DocflowReleaseRequest

    nutzer = {"sub": "verkauf-1", "roles": ["SALES_BEARBEITEN"]}

    def bestaetige(beleg: str, schluessel: str, version=None):
        return asyncio.run(confirm_document(beleg, DocflowReleaseRequest(idempotency_key=schluessel,
                                                                         expected_version=version),
                                            tenant_id=w["mandant"], db=w["db"], nutzer=nutzer))

    beleg = _freigegeben(w)
    assert bestaetige(beleg, "rest-ab-0001", 2).command == "confirm"
    with pytest.raises(HTTPException) as konflikt:
        bestaetige(_beleg(w), "rest-ab-0002")  # Entwurf
    assert konflikt.value.status_code == 409
    with pytest.raises(HTTPException) as unbekannt:
        bestaetige(str(uuid.uuid4()), "rest-ab-0003")
    assert unbekannt.value.status_code in (403, 404)
