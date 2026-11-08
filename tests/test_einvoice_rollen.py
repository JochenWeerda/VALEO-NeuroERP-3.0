"""Die E-Rechnungswege pruefen die Belegrolle.

Bis 14.10.2026 genuegte eine Anmeldung: Jede angemeldete Person des Mandanten konnte zu jeder eigenen Ausgangsrechnung
XRechnung und ZUGFeRD erzeugen und damit einen Eintrag im GoBD-Archiv festschreiben. Jetzt gilt wie bei
``/finance/invoices``: erzeugen (Archiveintrag) ``beleg_write``, abrufen ohne Archiveintrag ``beleg_read``.

Geprueft gegen die echte Datenbank.
"""

from __future__ import annotations

import json
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints.sales_invoice_einvoice import router
from app.core.database import SessionLocal
from testgrenze import ersetze_mandant, ersetze_nutzer

WEG = "/sales/invoices"


@pytest.fixture
def rechnung():
    mandant, nummer = f"er-{uuid.uuid4().hex[:8]}", f"ER-{uuid.uuid4().hex[:10]}"
    beleg = {"number": nummer, "tenantId": mandant, "status": "GEBUCHT", "date": "2026-10-14",
             "dueDate": "2026-11-14", "customerId": "K-1", "subtotalNet": 100, "totalTax": 19, "totalGross": 119,
             "lines": [{"article": "Weizen", "qty": 2, "price": 50, "vatRate": 19}]}
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO documents (id, doc_type, doc_number, data) VALUES (:id, 'sales_invoice', :n, CAST(:d AS jsonb))"),
            {"id": str(uuid.uuid4()), "n": nummer, "d": json.dumps(beleg)})
        db.commit()
    yield mandant, nummer
    with SessionLocal() as db:
        db.execute(text("DELETE FROM documents WHERE doc_number = :n"), {"n": nummer})
        db.commit()


def _als(mandant: str, *rollen: str) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    ersetze_nutzer(app, *rollen)
    ersetze_mandant(app, mandant)
    return TestClient(app, raise_server_exceptions=False)


def _archiveintraege(nummer: str) -> int:
    with SessionLocal() as db:
        return db.execute(text(
            "SELECT count(*) FROM domain_docflow.document_artifacts a "
            "JOIN domain_docflow.document_headers h ON h.id = a.header_id "
            "WHERE h.doc_type = 'sales_invoice' AND h.doc_number = :n"), {"n": nummer}).scalar()


def test_ohne_belegrolle_weder_erzeugen_noch_abrufen(rechnung):
    mandant, nummer = rechnung
    c = _als(mandant, "LAGER_BEARBEITEN")
    assert c.post(f"{WEG}/{nummer}/einvoice/xrechnung", json={}).status_code == 403
    assert c.post(f"{WEG}/{nummer}/einvoice/zugferd", json={}).status_code == 403
    assert c.get(f"{WEG}/{nummer}/einvoice/xrechnung").status_code == 403
    assert _archiveintraege(nummer) == 0


@pytest.mark.parametrize("rolle", ["SALES_LESEN", "FINANCE_LESEN"])
def test_eine_leserolle_ruft_ab_aber_erzeugt_nicht(rechnung, rolle):
    mandant, nummer = rechnung
    c = _als(mandant, rolle)
    assert c.get(f"{WEG}/{nummer}/einvoice/xrechnung").status_code == 200
    assert c.post(f"{WEG}/{nummer}/einvoice/xrechnung", json={}).status_code == 403
    assert c.post(f"{WEG}/{nummer}/einvoice/zugferd", json={}).status_code == 403
    assert _archiveintraege(nummer) == 0


def test_die_sachbearbeitung_erzeugt_und_archiviert(rechnung):
    mandant, nummer = rechnung
    antwort = _als(mandant, "SALES_BEARBEITEN").post(f"{WEG}/{nummer}/einvoice/xrechnung", json={})
    assert antwort.status_code == 200, antwort.text
    assert _archiveintraege(nummer) == 1
