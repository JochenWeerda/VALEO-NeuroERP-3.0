"""Einlagern des DocFlow-Wareneingangs bucht den Lagerzugang, Storno bucht ihn zurueck (BELEG-052 Phase 3b).

Vorher bewegte ein DocFlow-Wareneingang keinen Bestand; nur der alte Avis-Weg gegen den Altspeicher der Bestellungen
buchte ein. Freigabe und Umwandlung bleiben, wie sie sind; das Kommando ``einlagern`` des offenen Wareneingangs bucht
und schliesst ihn ab. Gegen echtes Schema, zurueckgerollt.
"""
from __future__ import annotations

import os
import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

pytestmark = pytest.mark.integration

DB_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe")


@pytest.fixture
def w(monkeypatch):
    from testgrenze import pruefstand_erlaubt

    try:
        engine = sa.create_engine(DB_URL, connect_args={"connect_timeout": 5, "application_name": "agent:claude"})
        verbindung = engine.connect()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    assert pruefstand_erlaubt(engine.url)
    aussen = verbindung.begin()
    s = Session(bind=verbindung, join_transaction_mode="create_savepoint")
    monkeypatch.setattr(s, "commit", s.flush)  # Freigabe/Storno committen - hier bleibt alles in der Testtransaktion
    t = f"we-{uuid.uuid4().hex[:8]}"
    lager, artikel = str(uuid.uuid4()), str(uuid.uuid4())
    s.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true)"), {"t": t})
    s.execute(sa.text("INSERT INTO domain_inventory.warehouses (id, warehouse_code, name, tenant_id, is_active) "
                      "VALUES (:id, 'HL-1', 'Halle 1', :t, true)"), {"id": lager, "t": t})
    s.execute(sa.text("INSERT INTO domain_inventory.articles (id, tenant_id, article_number, name, unit, current_stock) "
                      "VALUES (:id, :t, 'DUE-1', 'Kalkammonsalpeter', 'kg', 0)"), {"id": artikel, "t": t})
    try:
        yield {"db": s, "t": t, "lager": lager, "artikel": artikel}
    finally:
        s.close()
        aussen.rollback()
        verbindung.close()


def _wareneingang(w, *, artikel="DUE-1", einheit="dt", bausteine=None) -> str:
    from app.api.v1.schemas.docflow_schemas import DocflowCreateRequest, DocflowLineInput
    from app.services.docflow_service import DocflowService

    svc = DocflowService(w["db"], w["t"], "lager-1")
    kennung = svc.create_document(DocflowCreateRequest.model_validate({
        "doc_type": "goods_receipt", "doc_number": f"WE-{uuid.uuid4().hex[:6]}", "supplier_id": "L-1",
        "bausteine": bausteine,
        "items": [DocflowLineInput(article_number=artikel, quantity=12, unit=einheit, unit_price=0,
                                   charge="CH-7").model_dump()]}))
    svc.release(kennung, f"rel-{uuid.uuid4().hex}", None, None)
    return kennung


def _bestand(w) -> tuple[float, list]:
    stand = w["db"].execute(sa.text("SELECT current_stock FROM domain_inventory.articles WHERE id = :a"),
                            {"a": w["artikel"]}).scalar()
    bewegungen = w["db"].execute(sa.text(
        "SELECT movement_type, quantity, warehouse_id, charge, storno_ref IS NOT NULL FROM "
        "domain_inventory.inventory_stock_movements WHERE tenant_id = :t ORDER BY created_at, movement_type DESC"),
        {"t": w["t"]}).all()
    return float(stand), [tuple(b) for b in bewegungen]


def _status(w, kennung: str) -> str:
    return w["db"].execute(sa.text("SELECT status FROM domain_docflow.document_headers WHERE id = :id"),
                           {"id": kennung}).scalar()


def test_freigabe_bucht_nichts_einlagern_bucht_zugang_storno_bucht_zurueck(w):
    from app.api.v1.schemas.docflow_schemas import DocflowReverseRequest
    from app.services.docflow_service import DocflowService

    svc = DocflowService(w["db"], w["t"], "lager-1")
    we = _wareneingang(w)
    assert _bestand(w) == (0.0, [])  # die Freigabe allein lagert nichts ein
    schluessel = f"ein-{uuid.uuid4().hex}"
    ergebnis = svc.einlagern(we, "HL-1", schluessel, None)
    assert ergebnis["payload"]["warehouse_id"] == w["lager"]
    stand, bewegungen = _bestand(w)
    assert stand == 1200.0  # 12 dt in der Lagereinheit kg
    assert [(b[0], float(b[1]), b[2], b[3]) for b in bewegungen] == [("einlagerung", 1200.0, w["lager"], "CH-7")]
    assert _status(w, we) == "completed"

    svc.reverse_document(we, DocflowReverseRequest(idempotency_key=f"rev-{uuid.uuid4().hex}", reason="Falsch erfasst"))
    stand, bewegungen = _bestand(w)
    assert stand == 0.0
    assert sorted((b[0], float(b[1]), b[4]) for b in bewegungen) == [("abgang", 1200.0, True), ("einlagerung", 1200.0, False)]
    # Wiederholung desselben Auftrags bucht nicht doppelt (zuletzt: sie gibt die Sperre per Rollback frei).
    assert svc.einlagern(we, "HL-1", schluessel, None)["idempotent_hit"] is True


@pytest.mark.parametrize(("lager", "artikel", "einheit", "meldung"), [
    ("", "DUE-1", "dt", "ohne Lager"),
    ("HL-9", "DUE-1", "dt", "Lager HL-9"),
    ("HL-1", "GIBT-ES-NICHT", "dt", "Artikel GIBT-ES-NICHT"),
    ("HL-1", "DUE-1", "Stk", "Lagereinheit kg"),
])
def test_einlagern_ohne_buchbaren_zugang_bucht_nichts(w, lager, artikel, einheit, meldung):
    from app.core.exceptions import ValidationFailedError
    from app.services.docflow_service import DocflowService

    we = _wareneingang(w, artikel=artikel, einheit=einheit)
    with pytest.raises(ValidationFailedError, match=meldung):
        DocflowService(w["db"], w["t"], "lager-1").einlagern(we, lager, f"ein-{uuid.uuid4().hex}", None)
    assert _bestand(w) == (0.0, [])


def test_maskenaktion_einlagern_nimmt_das_lager_aus_dem_kopf(w):
    from app.services.docflow_belegaktionen import fuehre_aus, pruefe

    nutzer = {"sub": "lager-1", "roles": ["admin"]}
    ohne = _wareneingang(w)
    assert pruefe(w["db"], w["t"], "goods_receipt", ohne, "einlagern", nutzer, {})[0]["field"] == "lager"
    mit = _wareneingang(w, bausteine={"lager": {"lager": "HL-1"}})
    assert pruefe(w["db"], w["t"], "goods_receipt", mit, "einlagern", nutzer, {}) == []
    satz = fuehre_aus(w["db"], w["t"], "goods_receipt", mit, "einlagern", nutzer, {})
    assert "eingelagert" in satz
    assert _status(w, mit) == "completed"
    assert pruefe(w["db"], w["t"], "goods_receipt", mit, "einlagern", nutzer, {})[0]["message"].startswith("Die Aktion")


def test_rest_weg_lagert_ein_und_meldet_konflikt(w):
    """POST /docflow/{id}/store - mit Recht; ein zweites Einlagern ist ein Konflikt (zuletzt: es rollt zurueck)."""
    import asyncio

    from fastapi import HTTPException

    from app.api.v1.endpoints.docflow import store_goods_receipt
    from app.api.v1.schemas.docflow_schemas import DocflowStoreRequest

    nutzer = {"sub": "lager-1", "roles": ["LAGER_BEARBEITEN"]}

    def lagere(beleg: str, schluessel: str):
        return asyncio.run(store_goods_receipt(beleg, DocflowStoreRequest(idempotency_key=schluessel, lager="HL-1"),
                                               tenant_id=w["t"], db=w["db"], nutzer=nutzer))

    we = _wareneingang(w)
    assert lagere(we, "rest-we-0001").command == "store"
    assert _bestand(w)[0] == 1200.0
    with pytest.raises(HTTPException) as konflikt:
        lagere(we, "rest-we-0002")
    assert konflikt.value.status_code == 409


def _bestellung(w, nummer: str) -> str:
    from app.api.v1.schemas.docflow_schemas import DocflowCreateRequest, DocflowLineInput
    from app.services.docflow_service import DocflowService

    svc = DocflowService(w["db"], w["t"], "einkauf-1")
    kennung = svc.create_document(DocflowCreateRequest.model_validate({
        "doc_type": "purchase_order", "doc_number": f"E-{uuid.uuid4().hex[:6]}", "supplier_id": "L-1",
        "items": [DocflowLineInput(article_number="DUE-1", quantity=5, unit="dt", unit_price=30).model_dump()]}))
    svc.release(kennung, f"rel-{uuid.uuid4().hex}", None, None)
    w["db"].execute(sa.text("UPDATE domain_docflow.document_headers SET doc_number = :nr WHERE id = :id"),
                    {"nr": nummer, "id": kennung})
    return kennung


def test_wareneingang_aus_avis_wandelt_die_docflow_bestellung_und_lagert_ein(w):
    from app.services.wareneingang_avis_service import WareneingangAvisError, buche_wareneingang_aus_avis

    bestellung = _bestellung(w, "EK-AV-1")
    avis = str(uuid.uuid4())
    w["db"].execute(sa.text("INSERT INTO einkauf_anlieferavis (id, tenant_id, avis_nummer, bestell_nr, status) "
                            "VALUES (:id, :t, 'AV-1', 'EK-AV-1', 'ANGEKUENDIGT')"), {"id": avis, "t": w["t"]})
    ergebnis = buche_wareneingang_aus_avis(w["db"], avis, w["t"], "HL-1", " LS-77 ", "lager-1")
    assert (ergebnis["bestellung_id"], ergebnis["positionen"], ergebnis["lieferschein_nr"]) == (bestellung, 1, "LS-77")
    kopf = w["db"].execute(sa.text(
        "SELECT h.status, h.bausteine->'referenzen'->>'fremde_referenz', l.relation_type FROM "
        "domain_docflow.document_headers h JOIN domain_docflow.document_header_links l ON l.to_header_id = h.id "
        "WHERE h.id = :id"), {"id": ergebnis["wareneingang_id"]}).one()
    assert tuple(kopf) == ("completed", "LS-77", "order_to_receipt")
    assert _bestand(w)[0] == 500.0
    assert w["db"].execute(sa.text("SELECT status FROM einkauf_anlieferavis WHERE id = :id"),
                           {"id": avis}).scalar() == "ERHALTEN"
    with pytest.raises(WareneingangAvisError, match="nichts mehr offen"):
        buche_wareneingang_aus_avis(w["db"], avis, w["t"], "HL-1", "LS-78", "lager-1")
