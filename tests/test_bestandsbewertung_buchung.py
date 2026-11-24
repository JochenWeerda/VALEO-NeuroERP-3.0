"""Bestandskorrektur, Schwund und Inventur: Buchungsentwurf zum gleitenden Durchschnitt (M3, 24.11.2026).

Gegen die echte Datenbank in einer Transaktion, die am Ende zurueckrollt.
"""
from __future__ import annotations

import asyncio
import os
import uuid
from datetime import date
from decimal import Decimal

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.services.bestandsbewertung import BuchungNichtMoeglich, entwerfe_bestandsbuchung, gleitender_durchschnitt
from testgrenze import pruefstand_erlaubt

pytestmark = pytest.mark.integration
D = Decimal
DB_URL = os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL", "")


@pytest.fixture
def haus():
    try:
        engine = sa.create_engine(DB_URL, connect_args={"connect_timeout": 5, "application_name": "agent:claude"})
        verbindung = engine.connect()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    assert pruefstand_erlaubt(engine.url)
    aussen = verbindung.begin()
    s = Session(bind=verbindung, join_transaction_mode="create_savepoint")
    t = f"bwb-{uuid.uuid4().hex[:8]}"
    artikel, lager = str(uuid.uuid4()), str(uuid.uuid4())
    s.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true)"), {"t": t})
    s.execute(sa.text("INSERT INTO domain_inventory.articles (id, tenant_id, article_number, name, unit, warengruppe) "
                      "VALUES (:id, :t, 'WEIZEN', 'Weizen', 't', 'GETREIDE')"), {"id": artikel, "t": t})
    s.execute(sa.text("INSERT INTO domain_inventory.warehouses (id, tenant_id, warehouse_code, name) "
                      "VALUES (:id, :t, 'L1', 'Lager 1')"), {"id": lager, "t": t})
    for nummer, art in (("3980", "ASSET"), ("3400", "EXPENSE"), ("2800", "REVENUE")):
        s.execute(sa.text(
            "INSERT INTO domain_erp.chart_of_accounts (id, tenant_id, account_number, account_name, account_type, "
            "is_active, is_summary) VALUES (:id, :t, :n, :n, :a, TRUE, FALSE)"),
            {"id": str(uuid.uuid4()), "t": t, "n": nummer, "a": art})
    s.execute(sa.text(  # Zugang zum Einstandspreis: 10 t zu 200 EUR/t
        "INSERT INTO domain_inventory.inventory_stock_movements (id, tenant_id, article_id, warehouse_id, "
        "movement_type, quantity, unit, unit_cost, previous_stock, new_stock, movement_date, ownership_type, "
        "storage_fee_relevant) VALUES (:id, :t, :a, :w, 'einlagerung', 10, 't', 200, 0, 0, :d, 'owned', false)"),
        {"id": str(uuid.uuid4()), "t": t, "a": artikel, "w": lager, "d": date(2026, 11, 1)})
    s.commit()
    try:
        yield {"db": s, "t": t, "artikel": artikel, "lager": lager}
    finally:
        s.close()
        aussen.rollback()
        verbindung.close()


def _kontenzuordnung(h):
    h["db"].execute(sa.text(
        "INSERT INTO domain_einkauf.lager_kontenzuordnung (id, tenant_id, artikelgruppe, bestandskonto, "
        "gegenkonto_zugang, gegenkonto_abgang, aktiv) VALUES (:id, :t, 'GETREIDE', '3980', '2800', '3400', true)"),
        {"id": str(uuid.uuid4()), "t": h["t"]})
    h["db"].commit()


def _zeilen(h, eintrag: str) -> list[tuple[str, Decimal, Decimal]]:
    return [(r[0], D(str(r[1])), D(str(r[2]))) for r in h["db"].execute(sa.text(
        "SELECT a.account_number, l.debit_amount, l.credit_amount FROM domain_erp.journal_entry_lines l "
        "JOIN domain_erp.chart_of_accounts a ON a.id = l.account_id WHERE l.journal_entry_id = :e "
        "ORDER BY a.account_number"), {"e": eintrag}).fetchall()]


def _schwund(h, menge: float):
    from app.api.v1.endpoints.inventory_operations import SchwundBuchungIn, create_schwund

    return asyncio.run(create_schwund(SchwundBuchungIn(article_id=h["artikel"], warehouse_id=h["lager"], menge=menge),
                                      tenant_id=h["t"], db=h["db"]))


def test_schwund_ergibt_entwurf_zum_gleitenden_durchschnitt(haus):
    _kontenzuordnung(haus)

    antwort = _schwund(haus, 2)

    assert antwort.journal_entry_id
    status = haus["db"].execute(sa.text("SELECT status FROM domain_erp.journal_entries WHERE id = :e"),
                                {"e": antwort.journal_entry_id}).scalar_one()
    assert status == "draft"  # gebucht wird ueber den Freigabeweg des Hauptbuchs
    assert _zeilen(haus, antwort.journal_entry_id) == [("3400", D("400"), D("0")), ("3980", D("0"), D("400"))]


def test_mehrmenge_bucht_bestand_an_gegenkonto_zugang(haus):
    _kontenzuordnung(haus)

    eintrag = entwerfe_bestandsbuchung(haus["db"], haus["t"], "INV-TEST", "Inventur", date(2026, 11, 24),
                                       [(haus["artikel"], D("1.5"), "t")])

    assert _zeilen(haus, eintrag) == [("2800", D("0"), D("300")), ("3980", D("300"), D("0"))]


def test_ohne_kontenzuordnung_kein_entwurf_aber_bestand_gebucht(haus):
    antwort = _schwund(haus, 2)

    assert antwort.journal_entry_id is None
    assert gleitender_durchschnitt(haus["db"], haus["t"], haus["artikel"]).bestand == D("8")


def test_ohne_bepreisten_zugang_kein_entwurf(haus):
    _kontenzuordnung(haus)
    haus["db"].execute(sa.text("UPDATE domain_inventory.inventory_stock_movements SET unit_cost = NULL "
                               "WHERE tenant_id = :t"), {"t": haus["t"]})

    with pytest.raises(BuchungNichtMoeglich, match="kein gleitender Durchschnitt"):
        entwerfe_bestandsbuchung(haus["db"], haus["t"], "X", "X", date(2026, 11, 24), [(haus["artikel"], D(-1), "t")])


def test_positive_korrektur_erhoeht_den_bestand(haus):
    haus["db"].execute(sa.text(
        "INSERT INTO domain_inventory.inventory_stock_movements (id, tenant_id, article_id, warehouse_id, "
        "movement_type, quantity, unit, previous_stock, new_stock, movement_date, ownership_type, "
        "storage_fee_relevant) VALUES (:id, :t, :a, :w, 'adjustment', 5, 't', 0, 0, :d, 'owned', false)"),
        {"id": str(uuid.uuid4()), "t": haus["t"], "a": haus["artikel"], "w": haus["lager"], "d": date(2026, 11, 2)})

    schnitt = gleitender_durchschnitt(haus["db"], haus["t"], haus["artikel"])

    assert (schnitt.bestand, schnitt.preis) == (D("15"), D("200"))
