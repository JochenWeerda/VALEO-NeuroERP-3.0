"""Die Leser des Verkaufsauftrags lesen DocFlow direkt (BELEG-052, Schnitt S4).

Bis 17.11.2026 lasen Kreditlimit, Kunden-360, Verkaufsberichte, Management-Dashboard, Bestellvorschlag, Pickliste,
Referenzaufloesung und Kreditpruefung die Uebergangssicht der Auftraege. Gegen echtes Schema, zurueckgerollt.
"""
from __future__ import annotations

import asyncio
import os
import uuid
from datetime import date, timedelta

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import Session

pytestmark = pytest.mark.integration

DB_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe")


@pytest.fixture
def k(monkeypatch):
    from stammsaetze import lege_kunden_an
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
    t = f"s4-{uuid.uuid4().hex[:8]}"
    kunde, artikel = f"kunde-{uuid.uuid4().hex[:6]}", str(uuid.uuid4())
    s.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true)"), {"t": t})
    lege_kunden_an(s, t, kunde)
    s.execute(sa.text("INSERT INTO domain_inventory.articles (id, article_number, name, tenant_id, is_active) "
                      "VALUES (:id, 'WEI-S4', 'Weizen', :t, true)"), {"id": artikel, "t": t})
    try:
        yield {"db": s, "t": t, "kunde": kunde, "artikel": artikel}
    finally:
        s.close()
        aussen.rollback()
        verbindung.close()


def _svc(k):
    from app.services.docflow_service import DocflowService

    return DocflowService(k["db"], k["t"], "verkauf-1")


def _auftrag(k, menge: float = 10, preis: float = 20) -> tuple[str, str, str]:
    """Freigegebener Auftrag (10 dt zu 20, ohne Steuer: 200 brutto) mit Liefertermin."""
    from app.api.v1.schemas.docflow_schemas import DocflowCreateRequest, DocflowLineInput

    svc = _svc(k)
    kennung = svc.create_document(DocflowCreateRequest.model_validate({
        "doc_type": "sales_order", "doc_number": f"ENTWURF-{uuid.uuid4().hex[:6]}", "customer_id": k["kunde"],
        "items": [DocflowLineInput(article_number="WEI-S4", quantity=menge, unit="dt", unit_price=preis,
                                   tax_rate=0).model_dump()]}))
    k["db"].execute(sa.text("UPDATE domain_docflow.document_headers SET bausteine = CAST(:b AS jsonb) WHERE id = :id"),
                    {"id": kennung, "b": '{"lieferung": {"liefertermin": "2026-12-01"}}'})
    svc.release(kennung, f"rel-{uuid.uuid4().hex}", None, None)
    nummer = k["db"].execute(sa.text("SELECT doc_number FROM domain_docflow.document_headers WHERE id = :id"),
                             {"id": kennung}).scalar()
    position = k["db"].execute(sa.text("SELECT id FROM domain_docflow.document_items WHERE header_id = :id"),
                               {"id": kennung}).scalar()
    return kennung, nummer, str(position)


def _teil_lieferung(k, auftrag: str, position: str, menge: float) -> str:
    from app.api.v1.schemas.docflow_schemas import DocflowConvertRequest

    return str(_svc(k).convert(auftrag, DocflowConvertRequest(
        target_doc_type="sales_delivery", idempotency_key=f"conv-{uuid.uuid4().hex}",
        quantities_by_source_item_id={position: menge}))["target_doc_id"])


def test_kreditlimit_und_kreditpruefung_zaehlen_offene_auftraege(k):
    from app.api.v1.endpoints.credit_management import get_credit_status_data
    from app.services.sales_credit_service import SalesCreditService

    auftrag, nummer, _ = _auftrag(k)
    brutto = float(k["db"].execute(sa.text("SELECT total_gross FROM domain_docflow.document_headers WHERE id = :id"),
                                   {"id": auftrag}).scalar())
    stand = get_credit_status_data(k["db"], k["kunde"], k["t"])
    assert stand.current_exposure == pytest.approx(brutto)
    dienst = SalesCreditService(k["db"], k["t"])
    assert dienst._order(nummer)["order_number"] == nummer
    assert dienst._order(auftrag)["customer_name"].startswith("Testkunde")
    assert dienst._exposure(k["kunde"]) == pytest.approx(brutto)
    assert dienst._exposure(k["kunde"], exclude_order=nummer) == 0
    zeile = next(z for z in dienst.list_customers() if z.get("customer_id") == k["kunde"] or z.get("kunde_id") == k["kunde"])
    assert zeile


def test_bestellvorschlag_sieht_die_offene_menge_nach_teillieferung(k):
    from modules.einkauf.services.bestellvorschlag_service import _open_sales_quantity, engine_verkauf

    auftrag, _, position = _auftrag(k, menge=10)
    _teil_lieferung(k, auftrag, position, 4)
    assert _open_sales_quantity(k["db"], k["artikel"], k["t"]) == 6
    assert _open_sales_quantity(k["db"], k["artikel"], k["t"], von_datum=date(2026, 12, 2)) == 0  # Termin 01.12.
    assert _open_sales_quantity(k["db"], k["artikel"], k["t"], bis_datum=date(2026, 12, 1)) == 6
    zeilen = engine_verkauf(k["db"], tenant_id=k["t"])
    assert [(z["artikel_nr"], z["offene_auftraege"]) for z in zeilen] == [("WEI-S4", 6.0)]
    assert engine_verkauf(k["db"], tenant_id=k["t"], von_datum=date(2026, 12, 2)) == []
    assert len(engine_verkauf(k["db"], tenant_id=k["t"], von_datum=date(2026, 11, 1),
                              bis_datum=date(2026, 12, 1))) == 1


def test_berichte_und_dashboard_aus_docflow(k):
    from app.api.v1.endpoints.compat import management_dashboard
    from app.api.v1.endpoints.sales_reports import (
        get_monthly_revenue, get_sales_pipeline_kpi, get_sales_summary, get_top_articles, get_top_customers)

    _auftrag(k)
    heute = date.today()
    von, bis = heute - timedelta(days=1), heute + timedelta(days=1)
    zusammen = asyncio.run(get_sales_summary(von, bis, k["t"], k["db"]))
    zusammen = zusammen if isinstance(zusammen, dict) else zusammen.model_dump()
    assert any(v == 1 for v in zusammen.values()), zusammen
    kunden = asyncio.run(get_top_customers(von, bis, 10, k["t"], k["db"]))
    assert "Testkunde" in str(kunden)
    artikel = asyncio.run(get_top_articles(von, bis, 10, k["t"], k["db"]))
    assert "WEI-S4" in str(artikel)
    assert "1" in str(asyncio.run(get_monthly_revenue(von, bis, k["t"], k["db"])))
    assert asyncio.run(get_sales_pipeline_kpi(k["t"], k["db"]))
    dashboard = asyncio.run(management_dashboard(k["t"], k["db"]))
    assert "Testkunde" in str(dashboard) and "Weizen" in str(dashboard)


def test_kunden_360_pickliste_und_referenz(k):
    from app.api.v1.endpoints.crm_360 import get_customer_360, get_customer_screen_summary
    from app.api.v1.endpoints.crm_360_reads import _fetch_customer_tab_items
    from app.api.v1.endpoints.pick_lists import _own_order
    from app.services.customer_reference import resolve_reference

    auftrag, nummer, _ = _auftrag(k)
    ansicht = asyncio.run(get_customer_360(k["kunde"], k["t"], k["db"]))
    assert nummer in str(ansicht)
    assert asyncio.run(get_customer_screen_summary(k["kunde"], k["t"], k["db"]))
    _, zeilen = _fetch_customer_tab_items(k["db"], customer_id=k["kunde"], tenant_id=k["t"], tab_key="auftraege",
                                          kunden_nr=None)
    assert [z["order_number"] for z in zeilen] == [nummer]

    _own_order(k["db"], auftrag, k["t"])
    with pytest.raises(HTTPException):
        _own_order(k["db"], auftrag, "anderer-mandant")
    treffer = resolve_reference(k["db"], k["t"], "sales_order", auftrag)
    assert (treffer.found, treffer.number) == (True, nummer)
    assert resolve_reference(k["db"], "anderer-mandant", "sales_order", auftrag).found is False


def test_ist_aggregation_liest_den_docflow_auftrag(k):
    from app.services.ist_aggregation_service import DEFAULT_SOURCES

    quelle = DEFAULT_SOURCES[0]
    zeilen = k["db"].execute(sa.text(
        f"SELECT {quelle.qty_col} AS menge, {quelle.amount_col} AS betrag, {quelle.date_expr} AS datum "  # nosec B608
        f"FROM {quelle.header_table} h JOIN {quelle.item_table} i ON i.{quelle.join_key} = h.id "
        f"WHERE h.tenant_id = :t AND ({quelle.extra_where})"), {"t": k["t"]}).all()
    assert zeilen == []
    _auftrag(k)
    zeilen = k["db"].execute(sa.text(
        f"SELECT {quelle.qty_col} AS menge, {quelle.amount_col} AS betrag, {quelle.date_expr} AS datum "  # nosec B608
        f"FROM {quelle.header_table} h JOIN {quelle.item_table} i ON i.{quelle.join_key} = h.id "
        f"WHERE h.tenant_id = :t AND ({quelle.extra_where})"), {"t": k["t"]}).mappings().all()
    assert [(float(z["menge"]), float(z["betrag"]), z["datum"].date()) for z in zeilen] == [
        (10.0, 200.0, date(2026, 12, 1))]
