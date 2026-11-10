"""MCP sales.invoice.post: Rechnung aus dem DocFlow-Lieferschein (BELEG-052 Phase 2a, 10.11.2026).

Bis heute las das Werkzeug den Altspeicher domain_sales.delivery_notes und legte die Rechnung im alten Rechnungsspeicher
an. Jetzt: derselbe Weg wie die Belegmaske - DocFlow-Umwandlung Lieferschein -> Rechnung, Rechnungsdatum aus dem
freigegebenen Vorschlag, eine Transaktion mit Vorschlagsstand, Audit und Wiederholungsschutz.
"""
from __future__ import annotations

import json
import os
import uuid

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import Session

pytestmark = pytest.mark.integration

DB_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe")


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
    t, kunde = f"mr-{uuid.uuid4().hex[:8]}", str(uuid.uuid4())
    s.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true)"), {"t": t})
    from app.finance.steuerschluessel import richte_skr03_ein

    richte_skr03_ein(s, t)
    s.execute(sa.text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name) "
                      "VALUES (:id, :t, 'K-MR', 'Hof Rechnung')"), {"id": kunde, "t": t})
    s.flush()
    try:
        yield {"db": s, "t": t, "kunde": kunde}
    finally:
        s.close()
        aussen.rollback()
        verbindung.close()


def _lieferschein(w) -> str:
    from app.api.v1.schemas.docflow_schemas import DocflowCreateRequest, DocflowLineInput
    from app.services.docflow_service import DocflowService

    svc = DocflowService(w["db"], w["t"], "verkauf-1")
    ls = svc.create_document(DocflowCreateRequest.model_validate({
        "doc_type": "sales_delivery", "doc_number": f"E-{uuid.uuid4().hex[:6]}", "customer_id": w["kunde"],
        "items": [DocflowLineInput(article_number="W", quantity=10, unit="dt", unit_price=21.5,
                                   tax_code="3").model_dump()]}))
    svc.release(ls, f"rel-{uuid.uuid4().hex}", 1, None)
    return str(svc.fetch_header(ls)["doc_number"])


def _vorschlag(w, nummer: str, stand: str = "approved") -> str:
    kennung = str(uuid.uuid4())
    w["db"].execute(sa.text(
        "INSERT INTO public.agent_proposals (proposal_id, tenant_id, action_type, risk_level, approval_status, "
        "context_snapshot) VALUES (:id, :t, 'rechnung_vorschlag', 'high', :st, CAST(:snap AS json))"),
        {"id": kennung, "t": w["t"], "st": stand,
         "snap": json.dumps({"lieferschein_nr": nummer, "rechnungsdatum": "2026-11-05"})})
    return kennung


def _buche(w, vorschlag: str, schluessel: str = "mcp-rechnung-1"):
    from app.services.mcp_execution_service import ToolExecutionRequest, _post_invoice

    return _post_invoice(w["db"], ToolExecutionRequest(tool_name="sales.invoice.post", mode="execute",
                                                       idempotency_key=schluessel,
                                                       parameters={"proposal_id": vorschlag}), "agent-1", w["t"])


def test_freigegebener_vorschlag_wird_docflow_rechnung_aus_dem_lieferschein(w):
    nummer = _lieferschein(w)
    ergebnis = _buche(w, _vorschlag(w, nummer))
    assert ergebnis["success"] is True and ergebnis["posted"] is False
    kopf = w["db"].execute(sa.text(
        "SELECT doc_type, status, document_date::date AS datum, total_net FROM domain_docflow.document_headers "
        "WHERE id = :id"), {"id": ergebnis["invoice_id"]}).mappings().one()
    assert (kopf["doc_type"], kopf["status"], str(kopf["datum"])) == ("sales_invoice", "open", "2026-11-05")
    assert float(kopf["total_net"]) == 215.0
    verknuepft = w["db"].execute(sa.text(
        "SELECT relation_type FROM domain_docflow.document_links WHERE to_header_id = :id"),
        {"id": ergebnis["invoice_id"]}).scalars().all()
    assert set(verknuepft) == {"delivery_to_invoice"}


# Je Test ein Fehlerfall als letzter Schritt: Das Werkzeug rollt die Sitzung zurueck, auch den Testaufbau.
def test_unbekannter_lieferschein_wird_nicht_berechnet(w):
    with pytest.raises(HTTPException) as unbekannt:
        _buche(w, _vorschlag(w, "LS-GIBT-ES-NICHT"))
    assert unbekannt.value.status_code == 404


def test_nicht_freigegebener_vorschlag_wird_nicht_ausgefuehrt(w):
    with pytest.raises(HTTPException) as offen:
        _buche(w, _vorschlag(w, _lieferschein(w), stand="pending"), "mcp-rechnung-2")
    assert offen.value.status_code == 409
