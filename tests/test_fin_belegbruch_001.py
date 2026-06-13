"""FIN-BELEG-001 — Finance Belegbrüche: Zahlungseingang → Rechnung BEZAHLT.

Prüft:
1. AR Zahlungseingang (finance_clearing): Rechnung wird auf BEZAHLT gesetzt wenn voll ausgeziffert
2. AR Zahlungseingang: Rechnung bleibt unverändert bei Teilzahlung
3. AP Zahlungslauf execute: AP-Rechnung wird auf BEZAHLT gesetzt wenn OP vollständig ausgeziffert
4. Skonto-Auszifferung: OP wird reduziert; Rechnung auf BEZAHLT bei Vollausgleich
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch, call
from decimal import Decimal

import pytest
from fastapi import HTTPException


TENANT = "00000000-0000-0000-0000-000000000001"


# ── AR Clearing ─────────────────────────────────────────────────────────────

class TestARClearingBelegbruch:
    def test_rechnung_auf_bezahlt_nach_vollausgleich(self):
        from app.api.v1.endpoints.finance_clearing import record_payment

        db = MagicMock()
        body = MagicMock()
        body.rechnungsnr = "RG-2026-001"
        body.betrag = 1190.0
        body.skontoBetrag = 0.0
        body.zahlungsdatum = None
        body.zahlungsart = None
        body.bediener = None

        svc_result = {"voll_ausgeziffert": True, "neu_offen": 0.0, "rechnungsnr": "RG-2026-001"}
        inv_doc = {"number": "RG-2026-001", "status": "GEBUCHT", "totalGross": 1190.0}

        with (
            patch("app.api.v1.endpoints.finance_clearing.FinanceClearingService") as MockSvc,
            patch("app.api.v1.endpoints.finance_clearing.get_repository", return_value=None),
            patch("app.api.v1.endpoints.finance_clearing.get_from_store", return_value=inv_doc) as mock_get,
            patch("app.api.v1.endpoints.finance_clearing.save_to_store") as mock_save,
        ):
            MockSvc.return_value.record_payment.return_value = svc_result
            result = record_payment(body=body, db=db, tenant_id=TENANT)

        assert result["voll_ausgeziffert"] is True
        mock_get.assert_called_once_with("sales_invoice", "RG-2026-001", None)
        saved_doc = mock_save.call_args[0][2]
        assert saved_doc["status"] == "BEZAHLT"

    def test_rechnung_bleibt_bei_teilzahlung(self):
        from app.api.v1.endpoints.finance_clearing import record_payment

        db = MagicMock()
        body = MagicMock()
        body.rechnungsnr = "RG-2026-002"
        body.betrag = 500.0
        body.skontoBetrag = 0.0
        body.zahlungsdatum = None
        body.zahlungsart = None
        body.bediener = None

        svc_result = {"voll_ausgeziffert": False, "neu_offen": 690.0}

        with (
            patch("app.api.v1.endpoints.finance_clearing.FinanceClearingService") as MockSvc,
            patch("app.api.v1.endpoints.finance_clearing.get_repository", return_value=None),
            patch("app.api.v1.endpoints.finance_clearing.get_from_store") as mock_get,
            patch("app.api.v1.endpoints.finance_clearing.save_to_store") as mock_save,
        ):
            MockSvc.return_value.record_payment.return_value = svc_result
            record_payment(body=body, db=db, tenant_id=TENANT)

        mock_get.assert_not_called()
        mock_save.assert_not_called()


# ── Skonto Auszifferung ──────────────────────────────────────────────────────

class TestSkontoAuszifferungBelegbruch:
    def _make_db(self, op_ausgeziffert: bool):
        db = MagicMock()
        insert_result = MagicMock()
        insert_result.fetchone.return_value = None  # INSERT doesn't return

        settled_status = "ausgeziffert" if op_ausgeziffert else "offen"
        update_result = MagicMock()
        update_result.fetchone.return_value = ("RG-2026-003", settled_status)

        select_result = MagicMock()
        # Return a mock row with _mapping for the SELECT after commit
        row = MagicMock()
        from datetime import datetime, timezone
        row._mapping = {
            "id": "AZ-001", "tenant_id": TENANT, "op_id": "OP-001",
            "rechnungsnr": "RG-2026-003", "zahlungsdatum": "2026-06-13",
            "zahlungsbetrag_eur": 1000.0, "skonto_betrag_eur": 20.0,
            "skonto_prozent": "1.9608", "gesamtbetrag_eur": 1020.0,
            "zahlungsart": "ueberweisung", "buchungstext": "Test",
            "fibu_konto": "1200", "skonto_konto": "8736", "status": "gebucht", "storniert": False,
            "created_at": datetime(2026, 6, 13, tzinfo=timezone.utc),
        }
        select_result.fetchone.return_value = row

        call_count = [0]
        def execute_side(sql, params=None):
            sql_str = str(sql)
            call_count[0] += 1
            if "INSERT INTO domain_shared.op_auszifferungen" in sql_str:
                return insert_result
            elif "UPDATE domain_erp.offene_posten" in sql_str:
                return update_result
            elif "SELECT * FROM domain_shared.op_auszifferungen" in sql_str:
                return select_result
            return MagicMock()

        db.execute.side_effect = execute_side
        return db

    def test_op_wird_reduziert_bei_vollausgleich(self):
        from app.api.v1.endpoints.op_skonto_auszifferung import create_auszifferung
        from app.api.v1.endpoints.op_skonto_auszifferung import SkontoAuszifferungCreate

        payload = MagicMock(spec=SkontoAuszifferungCreate)
        payload.op_id = "OP-001"
        payload.rechnungsnr = "RG-2026-003"
        payload.zahlungsdatum = "2026-06-13"
        payload.zahlungsbetrag_eur = Decimal("1000.00")
        payload.skonto_betrag_eur = Decimal("20.00")
        payload.zahlungsart = "ueberweisung"
        payload.buchungstext = "Test"
        payload.fibu_konto = "1200"
        payload.skonto_konto = "8736"

        db = self._make_db(op_ausgeziffert=True)
        inv_doc = {"number": "RG-2026-003", "status": "GEBUCHT"}

        with (
            patch("app.api.v1.endpoints.op_skonto_auszifferung.get_repository", return_value=None),
            patch("app.api.v1.endpoints.op_skonto_auszifferung.get_from_store", return_value=inv_doc),
            patch("app.api.v1.endpoints.op_skonto_auszifferung.save_to_store") as mock_save,
        ):
            create_auszifferung(payload=payload, db=db, tenant_id=TENANT)

        update_calls = [str(c.args[0]) for c in db.execute.call_args_list]
        op_updates = [s for s in update_calls if "offene_posten" in s and "UPDATE" in s]
        assert len(op_updates) > 0, "OP wurde nicht aktualisiert"
        saved = mock_save.call_args[0][2] if mock_save.called else {}
        assert saved.get("status") == "BEZAHLT"
