"""SALES-RETURN-001 — Retoure anlegen: haelt Lieferschein- und Rechnungsbezug, schreibt keinen Altspeicher."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


TENANT = "00000000-0000-0000-0000-000000000001"


def _make_payload(dn_ref: str | None = "LS-2026-001", inv_ref: str | None = "RG-2026-100"):
    p = MagicMock()
    p.tenant_id = TENANT
    p.customer_id = "CUST-001"
    p.customer_name = "Testkunde"
    p.return_number = "RET-2026-001"
    p.delivery_note_reference = dn_ref
    p.invoice_reference = inv_ref
    p.reason = "Beschädigt"
    p.return_type = "Retoure"
    p.status = "draft"
    p.notes = ""
    p.model_dump = lambda exclude=None: {
        k: v for k, v in {
            "customer_id": "CUST-001", "customer_name": "Testkunde",
            "return_number": "RET-2026-001", "delivery_note_reference": dn_ref,
            "invoice_reference": inv_ref, "reason": "Beschädigt",
            "return_type": "Retoure", "status": "draft", "notes": "",
        }.items() if not exclude or k not in exclude
    }
    return p


class TestSalesReturnBelegbezug:
    @pytest.mark.asyncio
    async def test_retoure_haelt_ihre_bezuege_und_schreibt_keinen_altspeicher(self):
        """Lieferschein und Rechnung fuehrt DocFlow (BELEG-052): die Retoure schreibt nur sich selbst."""
        from app.api.v1.endpoints.sales_credit_notes import create_return

        db = MagicMock()
        with (
            patch("app.api.v1.endpoints.sales_credit_notes.assert_customer_allowed_for_delivery"),
            patch("app.api.v1.endpoints.sales_credit_notes.uuid7", return_value="RET-UUID-001"),
        ):
            ergebnis = await create_return(payload=_make_payload(), tenant_id=TENANT, db=db)

        sqls = [str(c.args[0]) for c in db.execute.call_args_list]
        assert not [s for s in sqls if "delivery_notes" in s or "sales_invoices" in s]
        assert len([s for s in sqls if "INSERT" in s.upper()]) == 1
        assert (ergebnis.delivery_note_reference, ergebnis.invoice_reference) == ("LS-2026-001", "RG-2026-100")
        assert db.commit.call_count == 1
