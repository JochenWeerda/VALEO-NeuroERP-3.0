"""Rechnung anlegen: Beleg, Buchung, offener Posten und Archiv in einem Commit.

Bis zum 08.10.2026 committete der Dokumentspeicher die Rechnung, bevor gebucht
wurde. Scheiterte die Buchung (oder der Archiveintrag), antwortete der Weg mit
500 — aber die Rechnung stand im Speicher, ohne Buchung und ohne offenen Posten,
und ein zweiter Versuch mit derselben Nummer ueberschrieb sie still.

Die Kundenpruefung ist hier ausgeblendet; sie ist nicht Gegenstand.
"""

from __future__ import annotations

import os
import uuid

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"),
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")

HAUS = f"rc-{uuid.uuid4().hex[:6]}"
WEG = "/api/v1/finance/invoices"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as v:
            v.execute(text("SELECT 1 FROM documents LIMIT 0"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    return motor


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def ohne_kundenpruefung(monkeypatch):
    from app.api.v1.endpoints import finance_invoices as modul

    monkeypatch.setattr(modul, "assert_customer_allowed_for_invoice", lambda *_a, **_k: None)


@pytest.fixture
def nummer(engine):
    from sqlalchemy import text

    nr = f"RE-{uuid.uuid4().hex[:10]}"
    yield nr
    with engine.begin() as v:
        v.execute(text("DELETE FROM documents WHERE doc_number = :n"), {"n": nr})


def gespeichert(engine, nr: str) -> int:
    from sqlalchemy import text

    with engine.connect() as v:
        return v.execute(text("SELECT count(*) FROM documents WHERE doc_number = :n"), {"n": nr}).scalar()


def rechnung(nr: str, status: str = "VERSENDET") -> dict:
    return {"number": nr, "date": "2026-10-08", "customerId": str(uuid.uuid4()), "dueDate": "2026-11-07",
            "status": status, "subtotalNet": 100.0, "totalTax": 19.0, "totalGross": 119.0}


def kopf() -> dict[str, str]:
    return {"X-Tenant-ID": HAUS, "Authorization": "Bearer dev-token"}


def test_scheitert_die_buchung_bleibt_keine_rechnung_zurueck(engine, client, nummer, monkeypatch):
    from app.api.v1.endpoints import finance_invoices as modul
    from app.core.exceptions import ValidationFailedError

    def buchung_scheitert(*_a, **_k):
        raise ValidationFailedError("Konto 1400 fehlt")

    monkeypatch.setattr(modul, "_post_sales_invoice_financials", buchung_scheitert)
    antwort = client.post(WEG, headers=kopf(), json=rechnung(nummer))
    assert antwort.status_code >= 400
    assert gespeichert(engine, nummer) == 0


def test_scheitert_das_archiv_bleibt_keine_rechnung_zurueck(engine, client, nummer, monkeypatch):
    from app.api.v1.endpoints import finance_invoices as modul
    from app.core.gobd_artifact import GobdArtifactError

    monkeypatch.setattr(modul, "_post_sales_invoice_financials", lambda *_a, **_k: {})

    def archiv_scheitert(*_a, **_k):
        raise GobdArtifactError("Archiv nicht erreichbar")

    monkeypatch.setattr(modul, "register_artifact", archiv_scheitert)
    antwort = client.post(WEG, headers=kopf(), json=rechnung(nummer))
    assert antwort.status_code >= 400
    assert gespeichert(engine, nummer) == 0


def test_buchung_ohne_eigenen_commit(monkeypatch):
    """Die Buchung schreibt nicht vorab fest; den Commit macht der Rechnungsweg."""
    from app.api.v1.endpoints import finance_invoices as modul

    gesehen: dict = {}

    class Dienst:
        def __init__(self, db, tenant_id, *, commit=True):
            gesehen["commit"] = commit

        def post_ausgangsrechnung_with_op(self, **_k):
            return {}

    monkeypatch.setattr(modul, "SalesPostingService", Dienst)
    from app.documents.models import SalesInvoice

    modul._post_sales_invoice_financials(None, SalesInvoice(**rechnung("RE-X")), HAUS)
    assert gesehen["commit"] is False


def test_ein_entwurf_wird_gespeichert(engine, client, nummer):
    antwort = client.post(WEG, headers=kopf(), json=rechnung(nummer, status="ENTWURF"))
    assert antwort.status_code == 200, antwort.text
    assert gespeichert(engine, nummer) == 1
