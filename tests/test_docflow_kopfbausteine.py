"""DocFlow fuehrt die Kopfbausteine des Belegvertrags (BELEG-052, 09.11.2026).

Lieferung, Zahlung, Texte, Kontakt und Referenzen standen nur in den Eigenspeichern; die Belegmaske konnte sie nicht
pflegen. Jetzt: anlegen, aendern (je Baustein ersetzen, leer = entfernen), lesen (Belegvertrag und flacher Maskenkopf),
nur die Bausteine der Belegart und nur bekannte Felder - Unbekanntes wird abgelehnt, nicht verworfen.
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


@pytest.fixture
def db():
    try:
        engine = sa.create_engine(DB_URL, connect_args={"connect_timeout": 5, "application_name": "agent:claude"})
        verbindung = engine.connect()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    aussen = verbindung.begin()
    vorhanden = verbindung.execute(sa.text(
        "SELECT 1 FROM information_schema.columns WHERE table_schema = 'domain_docflow' "
        "AND table_name = 'document_headers' AND column_name = 'bausteine'")).scalar()
    if not vorhanden:
        spec = importlib.util.spec_from_file_location("m", WURZEL / "alembic/versions/docflow_kopfbausteine_20261109.py")
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        with Operations.context(MigrationContext.configure(verbindung)):
            modul.upgrade()
    sitzung = Session(bind=verbindung, join_transaction_mode="create_savepoint")
    mandant, kunde = f"kb-{uuid.uuid4().hex[:8]}", str(uuid.uuid4())
    sitzung.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true)"), {"t": mandant})
    from app.finance.steuerschluessel import richte_skr03_ein

    richte_skr03_ein(sitzung, mandant)
    sitzung.execute(sa.text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name) "
                            "VALUES (:id, :t, 'K-KB', 'Hof Baustein')"), {"id": kunde, "t": mandant})
    sitzung.flush()
    try:
        yield {"db": sitzung, "mandant": mandant, "kunde": kunde}
    finally:
        sitzung.close()
        aussen.rollback()
        verbindung.close()


def _auftrag(w, **mehr) -> str:
    from app.api.v1.schemas.docflow_schemas import DocflowCreateRequest, DocflowLineInput
    from app.services.docflow_service import DocflowService

    return DocflowService(w["db"], w["mandant"], "verkauf-1").create_document(DocflowCreateRequest.model_validate({
        "doc_type": "sales_order", "doc_number": f"AU-{uuid.uuid4().hex[:5]}", "customer_id": w["kunde"],
        "items": [DocflowLineInput(article_number="W", quantity=10, unit="dt", unit_price=21.5, tax_code="3").model_dump()],
        **mehr}))


def _kopf(w, beleg: str) -> dict:
    from app.core.belegvertrag import kopfbausteine_flach
    from app.services.docflow_belegadapter import lies_beleg
    from app.services.docflow_service import DocflowService

    beleg_ = lies_beleg(DocflowService(w["db"], w["mandant"], "verkauf-1"), beleg)
    return {"bausteine": beleg_.bausteine, "flach": kopfbausteine_flach(beleg_.bausteine)}


def test_auftrag_traegt_lieferung_zahlung_texte_aus_der_flachen_maskenform(db):
    beleg = _auftrag(db, **{"lieferung__liefertermin": "2026-12-01", "lieferung__lieferadresse": "Hof 3, Leer",
                            "zahlung__zahlungsbedingung": "14 Tage 2 %", "zahlung__skonto_prozent": 2,
                            "texte__betreff": "Weizen Ernte 2026", "texte__notiz": ""})
    kopf = _kopf(db, beleg)
    assert kopf["bausteine"] == {"lieferung": {"liefertermin": "2026-12-01", "lieferadresse": "Hof 3, Leer"},
                                 "zahlung": {"zahlungsbedingung": "14 Tage 2 %", "skonto_prozent": 2},
                                 "texte": {"betreff": "Weizen Ernte 2026"}}  # leeres Feld faellt weg
    assert kopf["flach"]["lieferung__liefertermin"] == "2026-12-01"


def test_aendern_ersetzt_je_baustein_und_leer_entfernt(db):
    from app.api.v1.schemas.docflow_schemas import DocflowUpdateRequest
    from app.services.docflow_service import DocflowService

    beleg = _auftrag(db, **{"lieferung__liefertermin": "2026-12-01", "texte__betreff": "Alt"})
    svc = DocflowService(db["db"], db["mandant"], "verkauf-1")
    svc.update_document(beleg, DocflowUpdateRequest.model_validate({
        "expected_version": 1, "idempotency_key": f"k-{uuid.uuid4().hex}",
        "texte__betreff": "Neu", "lieferung__liefertermin": ""}))
    assert _kopf(db, beleg)["bausteine"] == {"texte": {"betreff": "Neu"}}  # Lieferung geleert, Texte ersetzt


def test_fremder_baustein_und_unbekanntes_feld_werden_abgelehnt(db):
    from app.core.exceptions import ValidationFailedError

    with pytest.raises(ValidationFailedError, match="gehoert nicht zur Belegart"):
        _auftrag(db, bausteine={"kontrakt": {"nummer": "K-1"}})
    with pytest.raises(ValidationFailedError, match="kennt"):
        _auftrag(db, **{"lieferung__rampe": "3"})


def test_die_belegmaske_pflegt_die_bausteine_ihrer_belegart():
    from app.core.belegvertrag import KOPFBAUSTEINE
    from app.core.screen_definitions_beleg import build_beleg_screen_definition

    for art, bausteine in KOPFBAUSTEINE.items():
        definition = build_beleg_screen_definition(art)
        kopf = {f["key"] for t in definition["tabs"] if t["key"] == "kopf" for f in t["fields"]}
        bearbeiten = next(a for a in definition["actions"] if a["key"] == "bearbeiten")
        eingaben = {f["key"] for f in bearbeiten["inputFields"]}
        for name in bausteine:
            erwartet = {k for k in kopf if k.startswith(f"{name}__")}
            assert erwartet, (art, name)
            assert erwartet <= eingaben, (art, name)
    lieferschein = build_beleg_screen_definition("sales_delivery")
    assert not any(f["key"].startswith("zahlung__") for t in lieferschein["tabs"] for f in t.get("fields") or [])


def test_mcp_auftragsstatus_zaehlt_offene_positionen_aus_docflow(db):
    """sales.order.status liest den DocFlow-Auftrag, nicht mehr domain_crm.sales_orders (BELEG-052)."""
    from app.services.mcp_execution_service import _offene_auftragspositionen

    beleg = _auftrag(db)
    assert _offene_auftragspositionen(db["db"], db["mandant"], beleg) == 1
