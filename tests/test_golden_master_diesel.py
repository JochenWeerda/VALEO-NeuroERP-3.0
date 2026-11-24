"""Golden Master: realer Dieselbeleg (Artikel 220050, Liter, Preis je 100 Liter) - exakt reproduzieren.

Daten: ``tests/golden_master/diesel_220050.json`` (anonymisierter Geschaeftsvorfall aus einem produktiven
Warenwirtschaftssystem, Nutzer 24.11.2026). Erwartet: alle neun Positionsbetraege exakt, Belegsumme 660,10 EUR als
Summe der gerundeten Positionen - nicht 660,11 EUR aus der gerundeten Summe von 660,108 EUR.
"""
from __future__ import annotations

import json
import os
import uuid
from decimal import Decimal as D
from pathlib import Path

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.core.kaufmaennisch import belegsumme, durchschnittspreis, geld, positionsbetraege

FALL = json.loads((Path(__file__).parent / "golden_master" / "diesel_220050.json").read_text(encoding="utf-8"))
BEZUG = D(FALL["price_unit_quantity"])
POSITIONEN = [(tag, D(menge), D(preis), D(netto)) for tag, menge, preis, netto in FALL["positions"]]


@pytest.mark.unit
@pytest.mark.parametrize(("tag", "menge", "preis", "netto"), POSITIONEN, ids=[p[0] for p in POSITIONEN])
def test_jede_position_exakt(tag, menge, preis, netto):
    assert positionsbetraege(menge, preis, preisbezug=BEZUG).netto == netto


@pytest.mark.unit
def test_belegsumme_aus_gerundeten_positionen():
    betraege = [positionsbetraege(m, p, preisbezug=BEZUG).netto for _, m, p, _ in POSITIONEN]
    ungerundet = sum((m * p / BEZUG for _, m, p, _ in POSITIONEN), D("0"))

    assert sum((m for _, m, _, _ in POSITIONEN), D("0")) == D(FALL["expected_total_quantity"])
    assert belegsumme(betraege) == D(FALL["expected_total_net"])
    assert ungerundet == D(FALL["expected_unrounded_total_net"])
    assert geld(ungerundet) == D("660.11")  # die falsche Reihenfolge - bewusst anders
    assert durchschnittspreis(belegsumme(betraege), D(FALL["expected_total_quantity"]), BEZUG) == \
        D(FALL["expected_weighted_average_price"])


@pytest.mark.unit
def test_keine_gleitkommarechnung():
    with pytest.raises(TypeError, match="Decimal"):
        positionsbetraege(59.40, D("140.00"), preisbezug=BEZUG)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        positionsbetraege(D("1"), D("1"), preisbezug=D("0"))


DB_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe")


@pytest.fixture
def welt():
    from app.finance.steuerschluessel import richte_skr03_ein

    try:
        engine = sa.create_engine(DB_URL, connect_args={"connect_timeout": 5, "application_name": "agent:claude"})
        verbindung = engine.connect()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    aussen = verbindung.begin()
    db = Session(bind=verbindung, join_transaction_mode="create_savepoint")
    mandant, kunde = f"gm-{uuid.uuid4().hex[:8]}", str(uuid.uuid4())
    db.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true)"), {"t": mandant})
    richte_skr03_ein(db, mandant)
    db.execute(sa.text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name) "
                       "VALUES (:id, :t, 'kunde-gm', 'Lohnunternehmen Test')"), {"id": kunde, "t": mandant})
    db.flush()
    try:
        yield {"db": db, "mandant": mandant, "kunde": kunde}
    finally:
        db.close()
        aussen.rollback()
        verbindung.close()


@pytest.mark.integration
def test_docflow_rechnet_den_dieselbeleg_exakt(welt):
    from app.api.v1.schemas.docflow_schemas import DocflowConvertRequest, DocflowCreateRequest, DocflowLineInput
    from app.services.docflow_service import DocflowService

    dienst = DocflowService(welt["db"], welt["mandant"], "verkauf-1")
    auftrag = dienst.create_document(DocflowCreateRequest(
        doc_type="sales_order", doc_number=f"AU-GM-{uuid.uuid4().hex[:5]}", customer_id=welt["kunde"],
        items=[DocflowLineInput(article_number=FALL["artikel"], description=FALL["bezeichnung"], quantity=float(m),
                                unit="l", unit_price=float(p), price_unit_quantity=float(BEZUG), tax_code="3")
               for _, m, p, _ in POSITIONEN]))

    kopf = welt["db"].execute(sa.text("SELECT total_net FROM domain_docflow.document_headers WHERE id = :id"),
                              {"id": auftrag}).scalar_one()
    zeilen = welt["db"].execute(sa.text(
        "SELECT id, quantity, unit, price_unit_quantity, line_total_net FROM domain_docflow.document_items "
        "WHERE header_id = :id ORDER BY line_number"), {"id": auftrag}).mappings().all()

    assert D(str(kopf)) == D(FALL["expected_total_net"])
    assert [D(str(z["line_total_net"])) for z in zeilen] == [n for *_, n in POSITIONEN]
    assert {z["unit"] for z in zeilen} == {"l"}  # Menge bleibt in Litern
    assert [D(str(z["quantity"])) for z in zeilen] == [m for _, m, _, _ in POSITIONEN]

    lieferung = dienst.convert(auftrag, DocflowConvertRequest(
        target_doc_type="sales_delivery", idempotency_key=f"gm-{uuid.uuid4().hex}",
        quantities_by_source_item_id={str(z["id"]): float(z["quantity"]) for z in zeilen}))
    ziel = lieferung["target_doc_id"]
    folge = welt["db"].execute(sa.text(
        "SELECT price_unit_quantity, line_total_net FROM domain_docflow.document_items WHERE header_id = :id "
        "ORDER BY line_number"), {"id": ziel}).mappings().all()

    assert {D(str(z["price_unit_quantity"])) for z in folge} == {BEZUG}  # Preisbezug geht in die Folge
    assert sum((D(str(z["line_total_net"])) for z in folge), D("0")) == D(FALL["expected_total_net"])
