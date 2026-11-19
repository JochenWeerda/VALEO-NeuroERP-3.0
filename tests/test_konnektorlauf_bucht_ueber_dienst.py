"""Konnektorlaeufe (Lohn, Anlagen) buchen und stornieren ueber den Buchungsdienst (M3, Journal-Schreiber-Ratsche).

Bis 19.11.2026 gingen Buchung und Gegenbuchung roh ins Journal, ohne Sequenz und Hash, und jeder Auditeintrag
committete den Lauf halb. Gegen echtes Schema, zurueckgerollt.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import date
from decimal import Decimal

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

pytestmark = pytest.mark.integration

DB_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe")


@pytest.fixture
def k():
    from testgrenze import pruefstand_erlaubt

    try:
        engine = sa.create_engine(DB_URL, connect_args={"connect_timeout": 5, "application_name": "agent:claude"})
        verbindung = engine.connect()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    assert pruefstand_erlaubt(engine.url)
    aussen = verbindung.begin()
    s = Session(bind=verbindung, join_transaction_mode="create_savepoint")
    t = f"konn-{uuid.uuid4().hex[:8]}"
    s.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true)"), {"t": t})
    for nummer in ("4120", "1740"):
        s.execute(sa.text(
            "INSERT INTO domain_erp.chart_of_accounts (id, tenant_id, account_number, account_name, account_type, "
            "is_active, is_summary) VALUES (:id, :t, :n, :n, 'EXPENSE', TRUE, FALSE)"),
            {"id": str(uuid.uuid4()), "t": t, "n": nummer})
    s.commit()  # nur den Savepoint: die aeussere Transaktion rollt am Ende zurueck
    try:
        yield {"db": s, "t": t}
    finally:
        s.close()
        aussen.rollback()
        verbindung.close()


def _lauf(k, *, konto: str = "1740") -> str:
    lauf = str(uuid.uuid4())
    k["db"].execute(sa.text(
        "INSERT INTO domain_erp.fibu_connector_runs (id, tenant_id, connector_type, status) "
        "VALUES (:id, :t, 'PAYROLL', 'VALIDATED')"), {"id": lauf, "t": k["t"]})
    nutzlast = {"booking_date": "2026-10-15", "document_no": "LOHN-2026-10", "text": "Lohn Oktober",
                "lines": [{"account": "4120", "dc": "D", "amount": "3150.40"},
                          {"account": konto, "dc": "C", "amount": "3150.40"}]}
    k["db"].execute(sa.text(
        "INSERT INTO domain_erp.fibu_connector_run_items (id, run_id, line_no, payload, status, tenant_id) "
        "VALUES (:id, :lauf, 1, CAST(:p AS jsonb), 'OK', :t)"),
        {"id": str(uuid.uuid4()), "lauf": lauf, "p": json.dumps(nutzlast), "t": k["t"]})
    k["db"].commit()
    return lauf


def _koepfe(k) -> list[dict]:
    return [dict(z) for z in k["db"].execute(sa.text(
        "SELECT id, entry_number, status, source, reference, total_debit, sequence_number, hash_current, "
        "reversed_entry_id, period FROM domain_erp.journal_entries WHERE tenant_id = :t ORDER BY entry_number"),
        {"t": k["t"]}).mappings()]


def test_der_lauf_bucht_mit_stempel_und_storniert_per_gegenbuchung(k):
    from app.core.connectors.workflow import post_run, reverse_run

    lauf = _lauf(k)
    post_run(k["db"], lauf, k["t"])
    [kopf] = _koepfe(k)
    assert (kopf["entry_number"], kopf["status"], kopf["source"], kopf["reference"]) == (
        "LOHN-2026-10", "posted", "connector", lauf)
    assert kopf["total_debit"] == Decimal("3150.40") and kopf["period"] == "2026-10"
    assert kopf["sequence_number"] is not None and kopf["hash_current"]
    zeilen = k["db"].execute(sa.text(
        "SELECT c.account_number, l.debit_amount, l.credit_amount FROM domain_erp.journal_entry_lines l "
        "JOIN domain_erp.chart_of_accounts c ON c.id = l.account_id WHERE l.journal_entry_id = :id "
        "ORDER BY l.line_number"), {"id": kopf["id"]}).all()
    assert [tuple(z) for z in zeilen] == [("4120", Decimal("3150.40"), Decimal("0.00")),
                                        ("1740", Decimal("0.00"), Decimal("3150.40"))]

    reverse_run(k["db"], lauf, k["t"])
    original, storno = sorted(_koepfe(k), key=lambda z: z["entry_number"])
    assert original["status"] == "reversed" and original["reversed_entry_id"] == storno["id"]
    assert storno["entry_number"] == "STORNO-LOHN-2026-10" and storno["status"] == "posted"
    assert storno["hash_current"] and storno["sequence_number"] > kopf["sequence_number"]
    assert storno["period"] == date.today().strftime("%Y-%m")  # Storno in die laufende Periode
    stand = k["db"].execute(sa.text("SELECT status FROM domain_erp.fibu_connector_runs WHERE id = :id"),
                            {"id": lauf}).scalar_one()
    assert stand == "REVERSED"


def test_ein_unbekanntes_konto_bucht_den_lauf_nicht(k):
    from app.core.connectors.workflow import post_run

    lauf = _lauf(k, konto="9999")
    with pytest.raises(ValueError, match="9999"):
        post_run(k["db"], lauf, k["t"])
    assert _koepfe(k) == []
