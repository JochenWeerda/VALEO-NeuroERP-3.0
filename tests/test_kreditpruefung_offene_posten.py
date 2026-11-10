"""Kreditpruefung zaehlt die offenen Forderungen aus den offenen Posten (BELEG-052, 10.11.2026).

Gelesen wurde der alte Rechnungsspeicher domain_sales.sales_invoices - leer, seit Rechnungen in DocFlow entstehen.
Die Kreditpruefung sah keine einzige offene Forderung. Finance fuehrt die Forderung als offenen Posten.
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
def w():
    from testgrenze import pruefstand_erlaubt

    try:
        engine = sa.create_engine(DB_URL, connect_args={"connect_timeout": 5})
        verbindung = engine.connect()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    assert pruefstand_erlaubt(engine.url)
    aussen = verbindung.begin()
    s = Session(bind=verbindung, join_transaction_mode="create_savepoint")
    try:
        yield {"db": s, "t": f"kr-{uuid.uuid4().hex[:8]}", "fremd": f"kr-{uuid.uuid4().hex[:8]}",
               "kunde": str(uuid.uuid4())}
    finally:
        s.close()
        aussen.rollback()
        verbindung.close()


def _posten(w, mandant: str, offen: float) -> None:
    w["db"].execute(sa.text(
        "INSERT INTO domain_erp.offene_posten (id, tenant_id, rechnungsnr, konto_typ, kunde_id, betrag, open_amount, "
        "offen, op_status) VALUES (:id, :t, :nr, 'debitoren', :k, 1000, :o, :o, 'offen')"),
        {"id": str(uuid.uuid4()), "t": mandant, "nr": f"RE-{uuid.uuid4().hex[:6]}", "k": w["kunde"], "o": offen})


def test_offene_forderungen_kommen_aus_den_offenen_posten(w):
    from app.api.v1.endpoints.credit_management import get_credit_status_data

    _posten(w, w["t"], 1200)       # offen
    _posten(w, w["t"], 0)          # ausgeglichen
    _posten(w, w["fremd"], 9999)   # fremder Mandant
    status = get_credit_status_data(w["db"], w["kunde"], w["t"])
    assert status.current_exposure == pytest.approx(1200.0)
