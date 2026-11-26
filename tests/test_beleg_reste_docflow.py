"""Fachreste aus BELEG-052 S1-S3 und 3B, gegen echtes Schema, zurueckgerollt.

Ueberlieferung im Wareneingang, Bestellfall Innovation (Nachschau), Versandwege der Bestellung (Post, Portal, Fax
ohne Faxdienst), offenes Bestellobligo, Niederlassung am Beleg (Loeschpruefung), Zustellnachweis im Belegverlauf.
"""
from __future__ import annotations

import asyncio
import os
import uuid

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
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
    t = f"rest-{uuid.uuid4().hex[:8]}"
    lieferant = str(uuid.uuid4())
    s.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true)"), {"t": t})
    s.execute(sa.text("INSERT INTO domain_einkauf.lieferanten (id, tenant_id, lieferantennummer, firmenname, "
                      "fax_bestellung) VALUES (:id, :t, :nr, 'Raiffeisen Testlager', '+49441000000')"),
              {"id": lieferant, "t": t, "nr": f"L-{t}"})
    lege_lieferanten_an(s, t, lieferant)
    try:
        yield {"db": s, "t": t, "lieferant": lieferant}
    finally:
        s.close()
        aussen.rollback()
        verbindung.close()


def _svc(k):
    from app.services.docflow_service import DocflowService

    return DocflowService(k["db"], k["t"], "einkauf-1")


def _beleg(k, art: str, bausteine: str = "{}", menge: float = 20, preis: float = 480, partner: dict | None = None):
    from app.api.v1.schemas.docflow_schemas import DocflowCreateRequest, DocflowLineInput

    svc = _svc(k)
    kennung = svc.create_document(DocflowCreateRequest.model_validate({
        "doc_type": art, "doc_number": f"ENTWURF-{uuid.uuid4().hex[:6]}",
        **(partner if partner is not None else {"supplier_id": k["lieferant"]}),
        "items": [DocflowLineInput(article_number="RAPS-R", quantity=menge, unit="t", unit_price=preis).model_dump()]}))
    k["db"].execute(sa.text("UPDATE domain_docflow.document_headers SET bausteine = CAST(:b AS jsonb) WHERE id = :id"),
                    {"id": kennung, "b": bausteine})
    svc.release(kennung, f"rel-{uuid.uuid4().hex}", None, None)
    nummer = k["db"].execute(sa.text("SELECT doc_number FROM domain_docflow.document_headers WHERE id = :id"),
                             {"id": kennung}).scalar()
    position = k["db"].execute(sa.text("SELECT id FROM domain_docflow.document_items WHERE header_id = :id"),
                               {"id": kennung}).scalar()
    return kennung, nummer, str(position)


def _eingang(k, bestellung: str, position: str, menge: float) -> str:
    from app.api.v1.schemas.docflow_schemas import DocflowConvertRequest

    return str(_svc(k).convert(bestellung, DocflowConvertRequest(
        target_doc_type="goods_receipt", idempotency_key=f"conv-{uuid.uuid4().hex}",
        quantities_by_source_item_id={position: menge}))["target_doc_id"])


def test_ueberlieferung_wird_erfasst_und_gutgeschrieben(k):
    from app.services.procurement_match_service import ProcurementMatchService

    bestellung, nummer, position = _beleg(k, "purchase_order")
    _eingang(k, bestellung, position, 22)  # 22 t auf 20 t bestellt
    dienst = ProcurementMatchService(k["db"], k["t"])
    zeile = dienst.match_three_way(nummer)["positionen"][0]
    assert (zeile["status"], float(zeile["geliefert"])) == ("ueberliefert", 22.0)
    assert dienst.preview_ers(nummer)["ers_preview"]["betrag_netto"] == 960.0  # 2 t zu 480


def test_bestellfall_innovation_wird_nachgeschaut_und_geprueft(k):
    from app.core.belegvertrag import pruefe_kopfbausteine
    from app.services.procurement_service import ProcurementService

    with pytest.raises(ValueError, match="kein zulaessiger Wert"):
        pruefe_kopfbausteine("purchase_order", {"bestellfall": {"bestellfall": "irgendwas"}})
    assert pruefe_kopfbausteine("purchase_order", {"bestellfall": {"bestellfall": "innovation"}}) == {
        "bestellfall": {"bestellfall": "innovation"}}

    _beleg(k, "purchase_order", menge=5, preis=12)  # normaler Bestellfall: keine Probe
    probe, nummer, _ = _beleg(k, "purchase_order", menge=5, preis=12,
                              bausteine='{"bestellfall": {"bestellfall": "innovation", "hinweis": "Neue Sorte"}}')
    zeilen = ProcurementService(k["db"], k["t"]).innovationen_bewerten()
    assert [(z["bestellnummer"], z["hinweis"], z["stand"], z["testmenge"]) for z in zeilen] == [
        (nummer, "Neue Sorte", "wartet_auf_lieferung", 5.0)]


def test_versandwege_der_bestellung(k):
    from modules.einkauf.services.versand_service import versende_docflow_bestellung

    bestellung, nummer, _ = _beleg(k, "purchase_order")
    assert versende_docflow_bestellung(k["db"], k["t"], bestellung, kanal="post")["status"] == "manuell"
    assert versende_docflow_bestellung(k["db"], k["t"], bestellung, kanal="portal")["status"] == "veroeffentlicht"
    # Ohne Faxdienst: nichts gilt als versandt, nichts wird eingetragen.
    assert versende_docflow_bestellung(k["db"], k["t"], bestellung, kanal="fax")["status"] == "nicht_eingerichtet"
    with pytest.raises(ValueError, match="gibt es nicht"):
        versende_docflow_bestellung(k["db"], k["t"], bestellung, kanal="brieftaube")

    eintraege = k["db"].execute(sa.text(
        "SELECT kanal, status FROM domain_einkauf.bestellung_kommunikation WHERE bestellung_id = :b ORDER BY kanal"),
        {"b": bestellung}).all()
    assert [tuple(e) for e in eintraege] == [("portal", "veroeffentlicht"), ("post", "erfasst")]
    from app.services.bestell_kommunikation_service import veroeffentlichte_fuer_lieferant

    assert [z["bestellnummer"] for z in veroeffentlichte_fuer_lieferant(k["db"], k["t"], k["lieferant"])] == [nummer]


def test_offenes_bestellobligo(k):
    from app.api.v1.endpoints.einkauf_kpis import get_kpis

    bestellung, _, position = _beleg(k, "purchase_order", menge=20, preis=480)
    assert get_kpis(None, None, k["db"], k["t"])["offenes_bestellobligo_netto"] == 9600.0
    _eingang(k, bestellung, position, 15)
    assert get_kpis(None, None, k["db"], k["t"])["offenes_bestellobligo_netto"] == 2400.0  # 5 t offen
    _eingang(k, bestellung, position, 7)  # Ueberlieferung: nichts mehr offen, nicht negativ
    assert get_kpis(None, None, k["db"], k["t"])["offenes_bestellobligo_netto"] == 0.0


def test_niederlassung_mit_belegen_bleibt(k):
    from app.api.v1.endpoints.branches import delete_branch

    zweig, leer = str(uuid.uuid4()), str(uuid.uuid4())
    for kennung, nr in ((zweig, 7), (leer, 8)):
        k["db"].execute(sa.text("INSERT INTO domain_shared.branches (id, tenant_id, branch_number, name, is_active) "
                                "VALUES (:id, :t, :nr, :name, true)"), {"id": kennung, "t": k["t"], "nr": nr,
                                                                        "name": f"NL {nr}"})
    _beleg(k, "purchase_order", bausteine='{"organisation": {"niederlassung": "7"}}')
    with pytest.raises(HTTPException) as fehler:
        asyncio.run(delete_branch(zweig, k["t"], k["db"]))
    assert fehler.value.status_code == 409
    asyncio.run(delete_branch(leer, k["t"], k["db"]))
    assert k["db"].execute(sa.text("SELECT count(*) FROM domain_shared.branches WHERE id = :id"),
                           {"id": leer}).scalar() == 0


def test_zustellnachweis_steht_im_belegverlauf_des_lieferscheins(k):
    from app.api.v1.endpoints.logistics_tours import PodIn, save_pod
    from stammsaetze import lege_kunden_an

    lege_kunden_an(k["db"], k["t"], "kunde-pod")
    lieferschein, nummer, _ = _beleg(k, "sales_delivery", partner={"customer_id": "kunde-pod"}, preis=0)
    tour, stopp = str(uuid.uuid4()), str(uuid.uuid4())
    k["db"].execute(sa.text("INSERT INTO domain_logistics.tours (id, tenant_id, date, status) "
                            "VALUES (:id, :t, CURRENT_DATE, 'GEPLANT')"), {"id": tour, "t": k["t"]})
    k["db"].execute(sa.text("INSERT INTO domain_logistics.tour_stops (id, tour_id, stop_order, tenant_id, "
                            "delivery_note_ref, status) VALUES (:id, :tour, 1, :t, :ref, 'GEPLANT')"),
                    {"id": stopp, "tour": tour, "t": k["t"], "ref": nummer})
    save_pod(tour, stopp, PodIn(signature_base64="x", recipient_name="Hofstelle Meyer",
                                delivered_at="2026-11-17T10:00:00"), k["t"], k["db"])
    eintrag = k["db"].execute(sa.text(
        "SELECT payload FROM domain_docflow.document_command_log WHERE header_id = :h AND command = 'proof_of_delivery'"),
        {"h": lieferschein}).scalar()
    assert eintrag["empfaenger"] == "Hofstelle Meyer" and eintrag["stop_id"] == stopp


def test_bestellmaske_zeigt_bestellfall_organisation_und_versandwege():
    from app.core.screen_definitions_beleg import build_beleg_screen_definition

    bestellung = build_beleg_screen_definition("purchase_order")
    felder = {f["key"]: f for f in _alle_felder(bestellung)}
    assert [o["value"] for o in felder["bestellfall__bestellfall"]["options"]] == [
        "bestand_abgleich", "direktlieferung", "innovation"]
    assert "organisation__niederlassung" in felder
    versenden = next(a for a in bestellung["actions"] if a["key"] == "versenden")
    assert [o["value"] for o in versenden["inputFields"][0]["options"]] == ["email", "fax", "edi", "post", "portal"]
    rechnung = build_beleg_screen_definition("sales_invoice")
    assert "bestellfall__bestellfall" not in {f["key"] for f in _alle_felder(rechnung)}
    assert next(a for a in rechnung["actions"] if a["key"] == "versenden")["label"] == "Per E-Mail versenden"


def _alle_felder(knoten):
    if isinstance(knoten, dict):
        if "key" in knoten and "type" in knoten and "label" in knoten:
            yield knoten
        for wert in knoten.values():
            yield from _alle_felder(wert)
    elif isinstance(knoten, list):
        for wert in knoten:
            yield from _alle_felder(wert)


def test_innovation_nach_der_ersten_lieferung(k):
    from datetime import timedelta

    from app.core.business_time import business_today
    from app.services.procurement_service import ProcurementService

    artikel, lager = str(uuid.uuid4()), str(uuid.uuid4())
    k["db"].execute(sa.text("INSERT INTO domain_inventory.articles (id, article_number, name, tenant_id, is_active) "
                            "VALUES (:id, 'RAPS-R', 'Raps neu', :t, true)"), {"id": artikel, "t": k["t"]})
    k["db"].execute(sa.text("INSERT INTO domain_inventory.warehouses (id, warehouse_code, name, tenant_id) "
                            "VALUES (:id, :code, 'Testlager', :t)"), {"id": lager, "code": f"L-{k['t']}", "t": k["t"]})
    probe, _, _ = _beleg(k, "purchase_order", menge=10, preis=12,
                         bausteine='{"bestellfall": {"bestellfall": "innovation"}}')
    k["db"].execute(sa.text("UPDATE domain_docflow.document_headers SET document_date = NOW() - INTERVAL '40 days' "
                            "WHERE id = :id"), {"id": probe})  # bestellt vor 40 Tagen, geliefert vor 30
    # Geschaeftsdatum wie der Dienst (Europe/Berlin): date.today() laeuft in der CI in UTC und lag zwischen 23 und 24
    # Uhr UTC einen Tag hinter dem Dienst (26.11.2026: 31 statt 30 Tage).
    heute = business_today()
    vor_dreissig = heute - timedelta(days=30)
    for art, menge, tag in (("in", 10, vor_dreissig), ("out", -8, heute)):
        k["db"].execute(sa.text(
            "INSERT INTO domain_inventory.inventory_stock_movements (id, article_id, warehouse_id, movement_type, "
            "quantity, previous_stock, new_stock, tenant_id, movement_date) "
            "VALUES (:id, :a, :w, :art, :m, 0, 0, :t, :tag)"),
            {"id": str(uuid.uuid4()), "a": artikel, "w": lager, "art": art, "m": menge, "t": k["t"], "tag": tag})
    zeile = ProcurementService(k["db"], k["t"]).innovationen_bewerten()[0]
    assert (zeile["stand"], zeile["verkauft"], zeile["tage_im_regal"]) == ("aufnehmen", 8.0, 30)
