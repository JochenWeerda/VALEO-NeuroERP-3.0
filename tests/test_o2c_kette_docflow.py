"""Die Order-to-Cash-Kette liest DocFlow (BELEG-052, Schnitt S2).

Bis 15.11.2026 las der Dienst den Lieferschein-Altspeicher ``domain_sales.delivery_notes``, in den seit Phase 1b
niemand mehr schreibt: Jeder Auftrag stand ohne Lieferschein und ohne Rechnung da. Gegen echtes Schema, zurueckgerollt.
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
def k(monkeypatch):
    from stammsaetze import lege_kunden_an
    from testgrenze import pruefstand_erlaubt

    try:
        engine = sa.create_engine(DB_URL, connect_args={"connect_timeout": 5, "application_name": "agent:claude"})
        verbindung = engine.connect()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    assert pruefstand_erlaubt(engine.url)
    aussen = verbindung.begin()
    s = Session(bind=verbindung, join_transaction_mode="create_savepoint")
    monkeypatch.setattr(s, "commit", s.flush)  # Kommandos committen - hier bleibt alles in der Testtransaktion
    t = f"o2c-{uuid.uuid4().hex[:8]}"
    s.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true)"), {"t": t})
    lege_kunden_an(s, t, "kunde-o2c")
    try:
        yield {"db": s, "t": t}
    finally:
        s.close()
        aussen.rollback()
        verbindung.close()


def _svc(k):
    from app.services.docflow_service import DocflowService

    return DocflowService(k["db"], k["t"], "verkauf-1")


def _nummer(k, kennung: str) -> str:
    return k["db"].execute(sa.text("SELECT doc_number FROM domain_docflow.document_headers WHERE id = :id"),
                           {"id": kennung}).scalar()


def _auftrag(k) -> tuple[str, str]:
    """Freigegebener Auftrag; die Belegnummer vergibt die Freigabe."""
    from app.api.v1.schemas.docflow_schemas import DocflowCreateRequest, DocflowLineInput

    svc = _svc(k)
    kennung = svc.create_document(DocflowCreateRequest.model_validate({
        "doc_type": "sales_order", "doc_number": f"ENTWURF-{uuid.uuid4().hex[:6]}", "customer_id": "kunde-o2c",
        "items": [DocflowLineInput(article_number="WEI-1", quantity=10, unit="dt", unit_price=20).model_dump()]}))
    svc.release(kennung, f"rel-{uuid.uuid4().hex}", None, None)
    return kennung, _nummer(k, kennung)


def _wandle(k, quelle: str, ziel: str) -> str:
    from app.api.v1.schemas.docflow_schemas import DocflowConvertRequest

    ergebnis = _svc(k).convert(quelle, DocflowConvertRequest(target_doc_type=ziel,
                                                             idempotency_key=f"conv-{uuid.uuid4().hex}"))
    return str(ergebnis["target_doc_id"])


def test_kette_zeigt_lieferschein_und_rechnung_aus_docflow(k):
    from app.services.o2c_chain_service import O2CChainService

    auftrag, auftragsnummer = _auftrag(k)
    dienst = O2CChainService(k["db"], k["t"])
    nur_auftrag = dienst.trace(auftragsnummer)
    assert nur_auftrag["found"] and nur_auftrag["summary"]["status"] == "auftrag"
    assert [luecke["stufe"] for luecke in nur_auftrag["luecken"]] == ["angebot", "lieferschein"]

    lieferschein = _wandle(k, auftrag, "sales_delivery")
    geliefert = dienst.trace(auftrag)
    assert geliefert["summary"] == {**geliefert["summary"], "lieferscheine": 1, "rechnungen": 0, "status": "geliefert"}
    assert "Lieferung(en) ohne Rechnung." in [luecke["text"] for luecke in geliefert["luecken"]]

    rechnung = _wandle(k, lieferschein, "sales_invoice")
    nummer = _nummer(k, rechnung)
    berechnet = dienst.trace(auftragsnummer)
    assert berechnet["summary"]["status"] == "berechnet" and berechnet["summary"]["vollstaendig"] is True
    assert [n["stage"] for n in berechnet["kette"]] == ["auftrag", "lieferschein", "rechnung"]
    assert berechnet["kette"][1]["rechnung"] == nummer and berechnet["kette"][2]["ref"] == nummer
    assert berechnet["kunde"]

    zeile = next(z for z in dienst.list_orders() if z["order_number"] == auftragsnummer)
    assert (zeile["hat_lieferschein"], zeile["hat_rechnung"], zeile["vollstaendig"]) == (True, True, True)


def test_stornierter_lieferschein_zaehlt_nicht_und_fremder_mandant_sieht_nichts(k):
    from app.api.v1.schemas.docflow_schemas import DocflowReverseRequest
    from app.services.o2c_chain_service import O2CChainService

    auftrag, auftragsnummer = _auftrag(k)
    lieferschein = _wandle(k, auftrag, "sales_delivery")
    _svc(k).reverse_document(lieferschein, DocflowReverseRequest(idempotency_key=f"rev-{uuid.uuid4().hex}",
                                                                 reason="Falsch erfasst"))
    dienst = O2CChainService(k["db"], k["t"])
    assert dienst.trace(auftragsnummer)["summary"]["lieferscheine"] == 0
    zeile = next(z for z in dienst.list_orders() if z["order_number"] == auftragsnummer)
    assert zeile["hat_lieferschein"] is False

    assert O2CChainService(k["db"], "anderer-mandant").trace(auftragsnummer) == {
        "found": False, "detail": "Auftrag nicht auflösbar."}
    assert O2CChainService(k["db"], "anderer-mandant").list_orders() == []
