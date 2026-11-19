"""Die Leser der Bestellung lesen DocFlow (BELEG-052, Schnitt S3).

Bis 16.11.2026 lasen Compat-Liste, Artikelkontext, Einkaufs-KPIs, ORDRSP-Abgleich, Rechnungspruefung, der
Lieferanten-Reiter und das Lieferantenportal ``domain_einkauf.bestellungen`` - dort entsteht seit Phase 3b keine
Bestellung mehr. Gegen echtes Schema, zurueckgerollt.
"""
from __future__ import annotations

import asyncio
import os
import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

pytestmark = pytest.mark.integration

DB_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe")


@pytest.fixture
def k(monkeypatch):
    from stammsaetze import lege_lieferanten_an
    from testgrenze import pruefstand_erlaubt

    try:
        engine = sa.create_engine(DB_URL, connect_args={"connect_timeout": 5, "application_name": "agent:claude"})
        verbindung = engine.connect()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    assert pruefstand_erlaubt(engine.url)
    aussen = verbindung.begin()
    s = Session(bind=verbindung, join_transaction_mode="create_savepoint")
    monkeypatch.setattr(s, "commit", s.flush)  # Kommandos committen - hier bleibt alles in der Testtransaktion
    t = f"s3-{uuid.uuid4().hex[:8]}"
    lieferant, artikel = str(uuid.uuid4()), str(uuid.uuid4())
    s.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true)"), {"t": t})
    s.execute(sa.text("INSERT INTO domain_einkauf.lieferanten (id, tenant_id, lieferantennummer, firmenname) "
                      "VALUES (:id, :t, :nr, 'Testmuehle')"), {"id": lieferant, "t": t, "nr": f"L-{t}"})
    lege_lieferanten_an(s, t, lieferant)
    s.execute(sa.text("INSERT INTO domain_inventory.articles (id, article_number, name, tenant_id, is_active) "
                      "VALUES (:id, 'WEI-S3', 'Weizen', :t, true)"), {"id": artikel, "t": t})
    try:
        yield {"db": s, "t": t, "lieferant": lieferant, "artikel": artikel}
    finally:
        s.close()
        aussen.rollback()
        verbindung.close()


def _svc(k):
    from app.services.docflow_service import DocflowService

    return DocflowService(k["db"], k["t"], "einkauf-1")


def _bestellung(k, menge: float = 10, preis: float = 25) -> tuple[str, str, str]:
    """Freigegebene Bestellung mit Liefertermin; liefert Kennung, Nummer und Positionskennung."""
    from app.api.v1.schemas.docflow_schemas import DocflowCreateRequest, DocflowLineInput

    svc = _svc(k)
    kennung = svc.create_document(DocflowCreateRequest.model_validate({
        "doc_type": "purchase_order", "doc_number": f"ENTWURF-{uuid.uuid4().hex[:6]}", "supplier_id": k["lieferant"],
        "items": [DocflowLineInput(article_number="WEI-S3", quantity=menge, unit="dt", unit_price=preis).model_dump()]}))
    k["db"].execute(sa.text("UPDATE domain_docflow.document_headers SET bausteine = CAST(:b AS jsonb) WHERE id = :id"),
                    {"id": kennung, "b": '{"lieferung": {"liefertermin": "2999-12-31"}, "texte": {"betreff": "Ernte"}}'})
    svc.release(kennung, f"rel-{uuid.uuid4().hex}", None, None)
    nummer = k["db"].execute(sa.text("SELECT doc_number FROM domain_docflow.document_headers WHERE id = :id"),
                             {"id": kennung}).scalar()
    position = k["db"].execute(sa.text("SELECT id FROM domain_docflow.document_items WHERE header_id = :id"),
                               {"id": kennung}).scalar()
    return kennung, nummer, str(position)


def _wareneingang(k, bestellung: str, position: str, menge: float) -> str:
    from app.api.v1.schemas.docflow_schemas import DocflowConvertRequest

    return str(_svc(k).convert(bestellung, DocflowConvertRequest(
        target_doc_type="goods_receipt", idempotency_key=f"conv-{uuid.uuid4().hex}",
        quantities_by_source_item_id={position: menge}))["target_doc_id"])


def test_compat_liste_und_suche_zeigen_die_docflow_bestellung(k):
    from app.api.v1.endpoints.compat import _bestellung_finden, _bestellungen_als_compat

    kennung, nummer, _ = _bestellung(k)
    zeile = next(z for z in _bestellungen_als_compat(k["db"], k["t"]) if z["id"] == kennung)
    assert (zeile["purchaseOrderNumber"], zeile["supplierName"], zeile["herkunft"]) == (nummer, "Testmuehle", "docflow")
    assert (zeile["subject"], zeile["deliveryDate"], zeile["subtotal"]) == ("Ernte", "2999-12-31", 250.0)
    assert _bestellung_finden(k["db"], k["t"], nummer)["id"] == kennung
    assert _bestellung_finden(k["db"], "anderer-mandant", nummer) is None


def test_artikelkontext_zeigt_offene_menge_und_einkaufspreis(k):
    from app.api.v1.endpoints.articles import get_article_position_context

    kennung, nummer, position = _bestellung(k, menge=10, preis=25)
    _wareneingang(k, kennung, position, 4)
    kontext = asyncio.run(get_article_position_context(k["artikel"], None, k["t"], k["db"]))
    kontext = kontext if isinstance(kontext, dict) else kontext.model_dump()
    assert kontext["incoming_orders"]["orders"] == [{"order_number": nummer, "quantity": 6.0,
                                                     "expected_date": "2999-12-31"}]
    assert kontext["purchase_pricing"]["last_purchase_price"] == 25.0


def test_einkaufs_kpis_aus_docflow(k):
    from app.api.v1.endpoints.einkauf_kpis import get_kpis

    kennung, _, position = _bestellung(k, menge=10, preis=25)
    _wareneingang(k, kennung, position, 4)
    kpis = get_kpis(None, None, k["db"], k["t"])
    assert kpis["fill_rate"] == pytest.approx(0.4)
    assert kpis["on_time_delivery_rate"] == 1.0  # zugesagt 2999-12-31
    assert kpis["avg_lead_time_days"] == 0.0
    assert kpis["top_5_suppliers_by_spend"] == [{"supplier_id": k["lieferant"], "total_spend": 250.0}]
    assert kpis["abc_analysis"]["C"]["count"] == 1  # ein Lieferant mit 100 %


def test_ordrsp_und_rechnungspruefung_lesen_die_docflow_belege(k):
    from app.api.v1.endpoints.einkauf_ab_erfassung import _bestellpositionen
    from app.api.v1.endpoints.purchase_invoice_verification import (
        _fetch_gr_amount, _fetch_invoice_amount, _fetch_po_amount)

    kennung, _, position = _bestellung(k)
    positionen = _bestellpositionen(k["db"], k["t"], {"id": kennung, "herkunft": "docflow"})
    assert [(p["pos_nr"], p["artikel_nr"], float(p["menge"])) for p in positionen] == [(1, "WEI-S3", 10.0)]
    assert _bestellpositionen(k["db"], k["t"], {"id": kennung, "herkunft": "dokumentspeicher"}) is None

    wareneingang = _wareneingang(k, kennung, position, 10)
    assert _fetch_po_amount(k["db"], kennung, k["t"]) == 250.0
    assert _fetch_gr_amount(k["db"], wareneingang, k["t"]) == 250.0
    assert _fetch_invoice_amount(k["db"], kennung, k["t"]) is None  # eine Bestellung ist keine Rechnung


def test_lieferantenreiter_und_portal_zeigen_die_docflow_bestellung(k):
    from app.services.bestell_kommunikation_service import liste, veroeffentlichte_fuer_lieferant
    from app.services.mask_rollout_summary_service import MaskRolloutSummaryService

    kennung, nummer, _ = _bestellung(k)
    seite = MaskRolloutSummaryService(k["db"], k["t"]).build_tab_data("einkauf/supplier", k["lieferant"], "bestellungen")
    assert [(z["bestell_nr"], z["betrag"]) for z in seite["items"]] == [(nummer, 250.0)]

    k["db"].execute(sa.text(
        "INSERT INTO domain_einkauf.bestellung_kommunikation (id, tenant_id, bestellung_id, kanal, betreff, status, "
        "versendet_am, erfasst_von) VALUES (:id, :t, :b, 'portal', 'Bestellung', 'veroeffentlicht', NOW(), 'test')"),
        {"id": str(uuid.uuid4()), "t": k["t"], "b": kennung})
    portal = veroeffentlichte_fuer_lieferant(k["db"], k["t"], k["lieferant"])
    assert [(z["bestellnummer"], z["liefertermin"], z["betrag_brutto"] > 0) for z in portal] == [
        (nummer, "2999-12-31", True)]
    assert [e["channel"] for e in liste(k["db"], k["t"], kennung)] == ["portal"]
    assert veroeffentlichte_fuer_lieferant(k["db"], "anderer-mandant", k["lieferant"]) == []
