"""Einzelabrufe des Dokumentspeichers treffen nur Belege des eigenen Mandanten.

Die Belegnummer ist im Speicher systemweit eindeutig. Bis 14.10.2026 lasen mehrere Wege per Nummer ohne Mandant:
die E-Rechnung erzeugte eine fremde Ausgangsrechnung mit den eigenen Absenderdaten, die Kopfdaten der
Eingangsrechnungsmaske zeigten fremde Rechnungen, Gutschrift und Retoure setzten eine fremde Rechnung auf
GUTGESCHRIEBEN, Zahlung und Storno setzten fremde Belege gleicher Nummer auf BEZAHLT bzw. STORNIERT, die
Memo-Verrechnung minderte offene Betraege und offene Posten fremder Eingangsrechnungen.

Lesewege gegen die echte Datenbank; die Statusnachtraege an der Speichergrenze.
"""

from __future__ import annotations

import json
import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import SessionLocal
from app.documents.router_helpers import eigener_beleg, get_repository
from testgrenze import ersetze_mandant, ersetze_nutzer


@pytest.fixture
def haus():
    mandant, anderer = f"ea-{uuid.uuid4().hex[:8]}", f"ea-{uuid.uuid4().hex[:8]}"
    nummern: list[str] = []

    def ablegen(art: str, wo: str | None, **daten) -> str:
        nummer = f"EA-{uuid.uuid4().hex[:10]}"
        beleg = {"status": "GEBUCHT", "date": "2026-10-14", "number": nummer, **daten}
        if wo is not None:
            beleg["tenantId"] = wo
        with SessionLocal() as db:
            db.execute(text(
                "INSERT INTO documents (id, doc_type, doc_number, data) VALUES (:id, :a, :n, CAST(:d AS jsonb))"),
                {"id": str(uuid.uuid4()), "a": art, "n": nummer, "d": json.dumps(beleg)})
            db.commit()
        nummern.append(nummer)
        return nummer

    yield {"mandant": mandant, "anderer": anderer, "ablegen": ablegen}
    with SessionLocal() as db:
        db.execute(text("DELETE FROM documents WHERE doc_number = ANY(:n)"), {"n": nummern})
        db.commit()


def test_eigener_beleg_liefert_nur_den_eigenen(haus):
    eigen = haus["ablegen"]("sales_invoice", haus["mandant"])
    fremd = haus["ablegen"]("sales_invoice", haus["anderer"])
    alt = haus["ablegen"]("sales_invoice", None)
    with SessionLocal() as db:
        repo = get_repository(db)
        assert eigener_beleg("sales_invoice", eigen, haus["mandant"], repo)["number"] == eigen
        assert eigener_beleg("sales_invoice", fremd, haus["mandant"], repo) is None
        assert eigener_beleg("sales_invoice", alt, haus["mandant"], repo) is None
        assert eigener_beleg("sales_invoice", eigen, "", repo) is None


def test_die_e_rechnung_entsteht_nur_aus_der_eigenen_rechnung(haus):
    from app.api.v1.endpoints.sales_invoice_einvoice import router

    zeile = {"customerId": "K-1", "dueDate": "2026-11-14", "subtotalNet": 100, "totalTax": 19, "totalGross": 119,
             "lines": [{"article": "Weizen", "qty": 2, "price": 50, "vatRate": 19}]}
    eigen = haus["ablegen"]("sales_invoice", haus["mandant"], **zeile)
    fremd = haus["ablegen"]("sales_invoice", haus["anderer"], **zeile)
    alt = haus["ablegen"]("sales_invoice", None, **zeile)

    app = FastAPI()
    app.include_router(router)
    ersetze_nutzer(app, "SALES_ADMIN")
    ersetze_mandant(app, haus["mandant"])
    c = TestClient(app, raise_server_exceptions=False)
    assert c.get(f"/sales/invoices/{eigen}/einvoice/xrechnung").status_code == 200
    assert c.get(f"/sales/invoices/{fremd}/einvoice/xrechnung").status_code == 404
    assert c.get(f"/sales/invoices/{alt}/einvoice/xrechnung").status_code == 404


def test_die_eingangsrechnungsmaske_zeigt_keine_fremde_rechnung(haus):
    from app.services.mask_rollout_summary_service import MaskRolloutSummaryService

    eigen = haus["ablegen"]("ap_invoice", haus["mandant"], totalGross=10)
    fremd = haus["ablegen"]("ap_invoice", haus["anderer"], totalGross=10)
    alt = haus["ablegen"]("ap_invoice", None, totalGross=10)
    with SessionLocal() as db:
        dienst = MaskRolloutSummaryService(db, haus["mandant"])
        assert dienst.build_summary("finance/ap-invoice", eigen)["title"] == eigen
        for nummer in (fremd, alt):
            with pytest.raises(HTTPException) as fehler:
                dienst.build_summary("finance/ap-invoice", nummer)
            assert fehler.value.status_code == 404


# ── Statusnachtraege an der Speichergrenze ───────────────────────────────────

MANDANT = "00000000-0000-0000-0000-000000000001"


@pytest.mark.parametrize("wo", ["fremd", None])
@pytest.mark.asyncio
async def test_eine_gutschrift_schreibt_keine_fremde_rechnung_gut(wo):
    from app.api.v1.endpoints.sales_credit_notes import create_credit_note

    payload = MagicMock(tenant_id=MANDANT, customer_id="K-1", customer_name="K", invoice_reference="RG-1",
                        reason="Retoure", currency="EUR", status="draft", notes="", lines=[],
                        credit_note_number="GS-1")
    rechnung = {"status": "OFFEN", "number": "RG-1", **({"tenantId": wo} if wo else {})}
    with (
        patch("app.api.v1.endpoints.sales_credit_notes.assert_customer_allowed_for_invoice"),
        patch("app.api.v1.endpoints.sales_credit_notes.get_repository", return_value=None),
        patch("app.documents.router_helpers.get_from_store", return_value=rechnung),
        patch("app.api.v1.endpoints.sales_credit_notes.save_to_store") as speichern,
        patch("app.api.v1.endpoints.sales_credit_notes.log_fibu_audit"),
        patch("app.api.v1.endpoints.sales_credit_notes._lege_an",
              return_value={"id": "CN-1", "total": 0, "netto": 0, "steuer": 0}),
        patch("app.api.v1.endpoints.sales_credit_notes.CreditNoteOut"),
    ):
        await create_credit_note(payload=payload, request=MagicMock(), tenant_id=MANDANT, db=MagicMock())
    speichern.assert_not_called()


@pytest.mark.parametrize("wo", ["fremd", None])
def test_ein_zahlungseingang_setzt_keine_fremde_rechnung_auf_bezahlt(wo):
    from app.api.v1.endpoints.finance_clearing import record_payment

    body = MagicMock(rechnungsnr="RG-2", betrag=10.0, skontoBetrag=0.0, zahlungsdatum=None, zahlungsart=None,
                     bediener=None)
    rechnung = {"status": "GEBUCHT", "number": "RG-2", **({"tenantId": wo} if wo else {})}
    with (
        patch("app.api.v1.endpoints.finance_clearing.FinanceClearingService") as dienst,
        patch("app.api.v1.endpoints.finance_clearing.get_repository", return_value=None),
        patch("app.documents.router_helpers.get_from_store", return_value=rechnung),
        patch("app.api.v1.endpoints.finance_clearing.save_to_store") as speichern,
    ):
        dienst.return_value.record_payment.return_value = {"voll_ausgeziffert": True}
        record_payment(body=body, db=MagicMock(), tenant_id=MANDANT)
    speichern.assert_not_called()
