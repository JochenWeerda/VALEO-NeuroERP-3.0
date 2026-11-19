"""Die Abgrenzung bucht ueber den kanonischen Buchungsdienst (M3, Journal-Schreiber-Ratsche).

Bis 19.11.2026 legte ``POST /accruals-provisions/{id}/post`` einen Journalkopf mit Status ``posted`` an - ohne eine
einzige Buchungszeile, ohne Periodenpruefung, ohne Sequenz und Hash. Gegen echtes Schema, zurueckgerollt.
"""
from __future__ import annotations

import asyncio
import os
import uuid
from datetime import date
from decimal import Decimal

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import Session

pytestmark = pytest.mark.integration

DB_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe")
NUTZER = {"sub": "buchhalter-abgrenzung"}


@pytest.fixture
def k(monkeypatch):
    from testgrenze import pruefstand_erlaubt

    try:
        engine = sa.create_engine(DB_URL, connect_args={"connect_timeout": 5, "application_name": "agent:claude"})
        verbindung = engine.connect()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    assert pruefstand_erlaubt(engine.url)
    aussen = verbindung.begin()
    s = Session(bind=verbindung, join_transaction_mode="create_savepoint")
    t = f"abgr-{uuid.uuid4().hex[:8]}"
    s.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true)"), {"t": t})
    for nummer, art in (("0980", "ASSET"), ("4900", "EXPENSE")):
        s.execute(sa.text(
            "INSERT INTO domain_erp.chart_of_accounts (id, tenant_id, account_number, account_name, account_type, "
            "is_active, is_summary) VALUES (:id, :t, :n, :n, :a, TRUE, FALSE)"),
            {"id": str(uuid.uuid4()), "t": t, "n": nummer, "a": art})
    # Die Sitzung arbeitet im Savepoint: commit loest nur ihn auf, die aeussere Transaktion rollt am Ende zurueck.
    # Ohne commit naehme das rollback() des Buchungswegs die Testdaten mit.
    s.commit()
    try:
        yield {"db": s, "t": t}
    finally:
        s.close()
        aussen.rollback()
        verbindung.close()


def _abgrenzung(k, *, konto: str = "0980", gegenkonto: str = "4900", periode: str = "2026-10") -> str:
    kennung = str(uuid.uuid4())
    k["db"].execute(sa.text(
        "INSERT INTO domain_erp.accruals_provisions (id, tenant_id, description, amount, account_number, "
        "counterpart_account, period, accrual_type) VALUES (:id, :t, 'Versicherung Vorauszahlung', 1200.50, :k, :g, "
        ":p, 'rechnungsabgrenzungsposten')"),
        {"id": kennung, "t": k["t"], "k": konto, "g": gegenkonto, "p": periode})
    k["db"].commit()
    return kennung


def _buche(k, kennung: str) -> dict:
    from app.api.v1.endpoints.accruals_provisions import post_accrual_provision

    return asyncio.run(post_accrual_provision(kennung, tenant_id=k["t"], db=k["db"], nutzer=NUTZER))


def _stand(k, kennung: str) -> str:
    return k["db"].execute(sa.text("SELECT status FROM domain_erp.accruals_provisions WHERE id = :id"),
                           {"id": kennung}).scalar_one()


def _journale(k) -> int:
    return k["db"].execute(sa.text("SELECT count(*) FROM domain_erp.journal_entries WHERE tenant_id = :t"),
                           {"t": k["t"]}).scalar_one()


def test_die_abgrenzung_bucht_soll_und_haben_mit_stempel(k):
    kennung = _abgrenzung(k)
    antwort = _buche(k, kennung)

    kopf = k["db"].execute(sa.text(
        "SELECT status, source, reference, posting_date, total_debit, total_credit, sequence_number, hash_current "
        "FROM domain_erp.journal_entries WHERE id = :id"), {"id": antwort["journal_entry_id"]}).mappings().one()
    assert kopf["status"] == "posted" and kopf["source"] == "accrual_provision"
    assert kopf["reference"] == f"ABGR-{kennung}"
    assert kopf["posting_date"] == date(2026, 10, 31)  # Stichtag Periodenende
    assert kopf["total_debit"] == kopf["total_credit"] == Decimal("1200.50")
    assert kopf["sequence_number"] is not None and kopf["hash_current"]

    zeilen = k["db"].execute(sa.text(
        "SELECT c.account_number, l.debit_amount, l.credit_amount FROM domain_erp.journal_entry_lines l "
        "JOIN domain_erp.chart_of_accounts c ON c.id = l.account_id WHERE l.journal_entry_id = :id "
        "ORDER BY l.line_number"), {"id": antwort["journal_entry_id"]}).all()
    assert [tuple(z) for z in zeilen] == [("0980", Decimal("1200.50"), Decimal("0.00")),
                                        ("4900", Decimal("0.00"), Decimal("1200.50"))]
    assert _stand(k, kennung) == "posted"


def test_eine_gebuchte_abgrenzung_bucht_nicht_zweimal(k):
    kennung = _abgrenzung(k)
    _buche(k, kennung)
    with pytest.raises(HTTPException) as fehler:
        _buche(k, kennung)
    assert fehler.value.status_code == 400
    assert _journale(k) == 1


def test_in_eine_gesperrte_periode_wird_nicht_gebucht(k):
    from app.services.finance_period_service import period_bounds

    beginn, ende = period_bounds("2026-10")
    k["db"].execute(sa.text(
        "INSERT INTO public.finance_accounting_periods (id, tenant_id, period, status, start_date, end_date) "
        "VALUES (:id, :t, '2026-10', 'CLOSED', :b, :e)"), {"id": str(uuid.uuid4()), "t": k["t"], "b": beginn, "e": ende})
    kennung = _abgrenzung(k)
    with pytest.raises(HTTPException) as fehler:
        _buche(k, kennung)
    assert fehler.value.status_code == 422 and "CLOSED" in fehler.value.detail
    assert _journale(k) == 0 and _stand(k, kennung) == "draft"


def test_ein_unbekanntes_konto_bucht_nichts(k):
    kennung = _abgrenzung(k, gegenkonto="9999")
    with pytest.raises(HTTPException) as fehler:
        _buche(k, kennung)
    assert fehler.value.status_code == 422
    assert _journale(k) == 0 and _stand(k, kennung) == "draft"


def test_eine_periode_ohne_monat_wird_abgewiesen(k):
    kennung = _abgrenzung(k, periode="Q4-2026")
    with pytest.raises(HTTPException) as fehler:
        _buche(k, kennung)
    assert fehler.value.status_code == 422
    assert _journale(k) == 0
