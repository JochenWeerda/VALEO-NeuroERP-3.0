"""Drei-Wege-Abgleich Bestellung - Wareneingang - Eingangsrechnung aus DocFlow (BELEG-052, Schnitt S3).

Referenzkette des Fahrplans (ERPNext als Massstab): Menge je Position aus der Umwandlung, Wert der Rechnung gegen den
gelieferten Wert, Abweichung sperrt. Bis 16.11.2026 las der Abgleich den Altspeicher der Bestellungen und einen
Wareneingangsspeicher, in den die Belegmaske nie schrieb: Jede DocFlow-Bestellung war "nicht aufloesbar".
Gegen echtes Schema, zurueckgerollt.
"""
from __future__ import annotations

import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

pytestmark = pytest.mark.integration


@pytest.fixture
def e(require_db, monkeypatch):
    from app.core.database import engine
    from testgrenze import pruefstand_erlaubt

    assert pruefstand_erlaubt(engine.url)
    verbindung = engine.connect()
    aussen = verbindung.begin()
    s = Session(bind=verbindung, join_transaction_mode="create_savepoint")
    monkeypatch.setattr(s, "commit", s.flush)  # Kommandos committen - hier bleibt alles in der Testtransaktion
    t = f"dwa-{uuid.uuid4().hex[:8]}"
    s.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true)"), {"t": t})
    try:
        yield {"db": s, "t": t}
    finally:
        s.close()
        aussen.rollback()
        verbindung.close()


def _svc(e):
    from app.services.docflow_service import DocflowService

    return DocflowService(e["db"], e["t"], "einkauf-1")


def _nummer(e, kennung: str) -> str:
    return e["db"].execute(sa.text("SELECT doc_number FROM domain_docflow.document_headers WHERE id = :id"),
                           {"id": kennung}).scalar()


def _bestellung(e) -> tuple[str, str, str]:
    """Freigegebene Bestellung ueber 10 dt zu 30 EUR; liefert Kennung, Nummer und Kennung der Position."""
    from app.api.v1.schemas.docflow_schemas import DocflowCreateRequest, DocflowLineInput

    svc = _svc(e)
    kennung = svc.create_document(DocflowCreateRequest.model_validate({
        "doc_type": "purchase_order", "doc_number": f"ENTWURF-{uuid.uuid4().hex[:6]}", "supplier_id": "L-1",
        "items": [DocflowLineInput(article_number="DUE-1", quantity=10, unit="dt", unit_price=30).model_dump()]}))
    svc.release(kennung, f"rel-{uuid.uuid4().hex}", None, None)
    position = e["db"].execute(sa.text("SELECT id FROM domain_docflow.document_items WHERE header_id = :id"),
                               {"id": kennung}).scalar()
    return kennung, _nummer(e, kennung), str(position)


def _wandle(e, quelle: str, ziel: str, mengen: dict | None = None) -> str:
    from app.api.v1.schemas.docflow_schemas import DocflowConvertRequest

    return str(_svc(e).convert(quelle, DocflowConvertRequest(
        target_doc_type=ziel, idempotency_key=f"conv-{uuid.uuid4().hex}",
        quantities_by_source_item_id=mengen or {}))["target_doc_id"])


def test_teillieferung_rechnung_und_preisabweichung(e):
    from app.services.procurement_match_service import ProcurementMatchService

    bestellung, nummer, position = _bestellung(e)
    abgleich = ProcurementMatchService(e["db"], e["t"])

    offen = abgleich.match_three_way(nummer)
    assert offen["found"] and offen["positionen"][0]["status"] == "offen"
    assert [a.get("code") for a in offen["ausnahmen"] if a.get("code")] == ["keine_rechnung"]
    assert offen["three_way"]["status"] == "ohne_bezug"

    wareneingang = _wandle(e, bestellung, "goods_receipt", {position: 4})
    teil = abgleich.match(bestellung)
    zeile = teil["positionen"][0]
    assert (zeile["status"], float(zeile["geliefert"]), float(zeile["offen"])) == ("teilgeliefert", 4.0, 6.0)
    assert zeile["wert_offen"] == 180.0  # 6 dt zu 30 EUR
    assert [w["gr_number"] for w in teil["wareneingaenge"]] == [_nummer(e, wareneingang)]
    assert next(z for z in abgleich.list_orders() if z["bestellnummer"] == nummer)["hat_wareneingang"] is True

    rechnung = _wandle(e, wareneingang, "purchase_invoice")
    stimmig = abgleich.match_three_way(nummer)
    assert [(r["rechnungsnummer"], r["quelle"], r["zugeordneter_lieferschein"]) for r in stimmig["rechnungen"]] == [
        (_nummer(e, rechnung), "docflow", _nummer(e, wareneingang))]
    assert stimmig["three_way"]["geliefert_wert"] == 120.0 and stimmig["three_way"]["fakturiert_netto"] == 120.0
    assert stimmig["three_way"]["status"] == "abgeglichen" and stimmig["summary"]["drei_wege_abgeglichen"] is True

    # Der Lieferant berechnet 33 statt 30 EUR: 10 % ueber dem gelieferten Wert - das sperrt.
    e["db"].execute(sa.text("UPDATE domain_docflow.document_headers SET total_net = 132, total_gross = 132 "
                            "WHERE id = :id"), {"id": rechnung})
    abweichung = abgleich.match_three_way(nummer)
    assert abweichung["three_way"]["status"] == "wertabweichung"
    assert abweichung["three_way"]["differenz"] == 12.0 and abweichung["summary"]["drei_wege_abgeglichen"] is False
    assert [a for a in abweichung["ausnahmen"] if a.get("code") == "rechnungswert_abweichung"][0]["schwere"] == "blocker"
    assert abweichung["ers_preview"]["berechtigt"] is True and abweichung["ers_preview"]["betrag_netto"] == 12.0


def test_stornierter_wareneingang_und_fremder_mandant(e):
    from app.api.v1.schemas.docflow_schemas import DocflowReverseRequest
    from app.services.procurement_match_service import ProcurementMatchService

    bestellung, nummer, position = _bestellung(e)
    wareneingang = _wandle(e, bestellung, "goods_receipt", {position: 10})
    abgleich = ProcurementMatchService(e["db"], e["t"])
    assert abgleich.match(nummer)["summary"]["vollstaendig_geliefert"] is True

    _svc(e).reverse_document(wareneingang, DocflowReverseRequest(idempotency_key=f"rev-{uuid.uuid4().hex}",
                                                                 reason="Falsche Lieferung"))
    nach_storno = abgleich.match(nummer)
    assert nach_storno["positionen"][0]["status"] == "offen" and nach_storno["wareneingaenge"] == []

    fremd = ProcurementMatchService(e["db"], "anderer-mandant")
    assert fremd.match(nummer) == {"found": False, "detail": "Bestellung nicht auflösbar."}
    assert fremd.list_orders() == []
