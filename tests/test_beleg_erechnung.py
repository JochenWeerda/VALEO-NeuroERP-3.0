"""E-Rechnung aus dem DocFlow-Beleg (BELEG-052 Phase 2, 10.11.2026).

Die XRechnung-Wege kannten nur den alten (leeren) Rechnungsspeicher; DocFlow-Rechnungen hatten keine E-Rechnung.
Jetzt: XRechnung aus dem Belegvertrag, erst ins GoBD-Archiv, dann lesbar; nur gebuchte Belege; Einheiten nach UN/ECE,
Unbekanntes wird nicht geraten; Wiederholung legt kein zweites Archivstueck an.
"""
from __future__ import annotations

import asyncio
import base64
import os
import uuid

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import Session

pytestmark = pytest.mark.integration

DB_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe")
NUTZER = {"sub": "verkauf-1", "roles": ["SALES_BEARBEITEN"]}


@pytest.fixture
def w():
    from testgrenze import pruefstand_erlaubt

    try:
        engine = sa.create_engine(DB_URL, connect_args={"connect_timeout": 5, "application_name": "agent:claude"})
        verbindung = engine.connect()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    assert pruefstand_erlaubt(engine.url)
    aussen = verbindung.begin()
    s = Session(bind=verbindung, join_transaction_mode="create_savepoint")
    t, kunde = f"er-{uuid.uuid4().hex[:8]}", str(uuid.uuid4())
    s.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, 'Landhandel Nord eG', true)"),
              {"t": t})
    from app.finance.steuerschluessel import richte_skr03_ein

    richte_skr03_ein(s, t)
    s.execute(sa.text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name) "
                      "VALUES (:id, :t, 'K-ER', 'Muehle Sued GmbH')"), {"id": kunde, "t": t})
    s.flush()
    try:
        yield {"db": s, "t": t, "kunde": kunde}
    finally:
        s.close()
        aussen.rollback()
        verbindung.close()


def _rechnung(w, einheit: str = "dt", gebucht: bool = True) -> str:
    from app.api.v1.schemas.docflow_schemas import DocflowCreateRequest, DocflowLineInput
    from app.services.docflow_service import DocflowService

    beleg = DocflowService(w["db"], w["t"], "verkauf-1").create_document(DocflowCreateRequest.model_validate({
        "doc_type": "sales_invoice", "doc_number": f"RE-{uuid.uuid4().hex[:6]}", "customer_id": w["kunde"],
        "items": [DocflowLineInput(article_number="W", description="Weizen A", quantity=10, unit=einheit,
                                   unit_price=21.5, tax_code="3").model_dump()]}))
    if gebucht:  # Buchen selbst prueft test_docflow_*; hier zaehlt der gebuchte Stand
        w["db"].execute(sa.text("UPDATE domain_docflow.document_headers SET status = 'posted' WHERE id = :id"),
                        {"id": beleg})
    w["db"].commit()  # nur der Sicherungspunkt; die aeussere Transaktion rollt am Ende zurueck
    return beleg


def _erzeuge(w, beleg: str):
    from app.api.v1.endpoints.beleg_erechnung import beleg_erechnung_erzeugen

    return asyncio.run(beleg_erechnung_erzeugen("sales_invoice", beleg, {"_mode": "execute"}, db=w["db"],
                                                tenant_id=w["t"], nutzer=NUTZER))


def _lese(w, beleg: str) -> dict:
    from app.api.v1.endpoints.beleg_erechnung import beleg_erechnung_lesen

    return beleg_erechnung_lesen("sales_invoice", beleg, db=w["db"], tenant_id=w["t"], nutzer=NUTZER)


def test_gebuchte_rechnung_wird_xrechnung_im_archiv(w):
    beleg = _rechnung(w)
    ergebnis = _erzeuge(w, beleg)
    assert ergebnis.success is True, ergebnis
    gelesen = _lese(w, beleg)
    xml = base64.b64decode(gelesen["xml"]).decode("utf-8")
    assert gelesen["dateiname"].startswith("XRechnung_")
    assert "Muehle Sued GmbH" in xml and "Landhandel Nord eG" in xml
    assert 'unitCode="DTN"' in xml  # 10 dt, nicht als Stueck
    # Wiederholung: kein zweites Archivstueck
    assert _erzeuge(w, beleg).success is True
    anzahl = w["db"].execute(sa.text(
        "SELECT count(*) FROM domain_docflow.document_artifacts WHERE header_id = :h AND artifact_type = 'xml'"),
        {"h": beleg}).scalar()
    assert anzahl == 1


def test_ungebuchte_rechnung_und_unbekannte_einheit_werden_abgelehnt(w):
    offen = _erzeuge(w, _rechnung(w, gebucht=False))
    assert offen.success is False and "gebuchten" in str(offen.validationErrors)
    fremd = _erzeuge(w, _rechnung(w, einheit="Fass"))
    assert fremd.success is False and "UN/ECE" in str(fremd.validationErrors)


def test_ohne_archiv_kein_download(w):
    with pytest.raises(HTTPException) as fehlt:
        _lese(w, _rechnung(w))
    assert fehlt.value.status_code == 404
