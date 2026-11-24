"""Journalstatus ist Pflicht - die Datenbank kennt nur die vier Status des Buchungsdienstes (24.11.2026).

Gegen die echte Datenbank in einer Transaktion, die am Ende zurueckrollt.
"""
from __future__ import annotations

import os
import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError

from app.services.finance_transaction_service import VALID_STATUSES

pytestmark = pytest.mark.integration
DB_URL = os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL", "")


@pytest.fixture
def verbindung():
    try:
        engine = sa.create_engine(DB_URL, connect_args={"connect_timeout": 5, "application_name": "agent:claude"})
        conn = engine.connect()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    aussen = conn.begin()
    mandant = f"js-{uuid.uuid4().hex[:8]}"
    conn.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true)"), {"t": mandant})
    try:
        yield conn, mandant
    finally:
        aussen.rollback()
        conn.close()


def _eintrag(conn, mandant: str, status_sql: str) -> str:
    kennung = str(uuid.uuid4())
    spalten = "id, tenant_id, entry_number, entry_date, posting_date, period" + (", status" if status_sql else "")
    werte = ":id, :t, :id, '2026-11-24', '2026-11-24', '2026-11'" + (f", {status_sql}" if status_sql else "")
    with conn.begin_nested():
        conn.execute(sa.text(f"INSERT INTO domain_erp.journal_entries ({spalten}) VALUES ({werte})"),  # nosec B608
                     {"id": kennung, "t": mandant})
    return kennung


def test_ohne_status_wird_entwurf(verbindung):
    conn, mandant = verbindung
    kennung = _eintrag(conn, mandant, "")

    assert conn.execute(sa.text("SELECT status FROM domain_erp.journal_entries WHERE id = :id"),
                        {"id": kennung}).scalar_one() == "draft"


@pytest.mark.parametrize("status_sql", ["NULL", "'pending'", "'POSTED'", "'gebucht'"])
def test_unbekannter_oder_leerer_status_abgewiesen(verbindung, status_sql):
    conn, mandant = verbindung

    with pytest.raises(IntegrityError):
        _eintrag(conn, mandant, status_sql)


def test_datenbank_und_dienst_kennen_dieselben_status(verbindung):
    conn, _ = verbindung
    bedingung = conn.execute(sa.text(
        "SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname = 'ck_journal_entries_status'")).scalar_one()

    assert {s for s in VALID_STATUSES if f"'{s}'" in bedingung} == VALID_STATUSES
