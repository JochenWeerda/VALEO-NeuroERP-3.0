"""SALES-O2C-001 — Order-to-Cash Completion: DN delivered → Auftrag auf geliefert.

Prüft:
1. deliver_delivery_note setzt Auftrag auf geliefert wenn vollständig geliefert
2. deliver_delivery_note lässt Auftrag in Ruhe wenn nur teilgeliefert
3. deliver_delivery_note wirft 400 wenn Status != shipped
4. sales_order_id wird bei DeliveryNote-Create gesetzt
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException


TENANT = "00000000-0000-0000-0000-000000000001"
LS_ID = "LS-001"
ORDER_ID = "ORD-001"


def _make_dn_mapping(status: str, sales_order_id: str | None = ORDER_ID):
    """Returns a mapping-like object that dict() can convert correctly."""
    data = {
        "status": status,
        "sales_order_id": sales_order_id,
        "delivery_note_number": "VK-2026-001",
        "customer_id": "CUST-1",
        "id": LS_ID,
        "tenant_id": TENANT,
        "branch_id": None,
        "sales_rep_id": None,
        "operator_id": None,
        "delivery_date": date(2026, 6, 13),
        "delivery_time": None,
        "cost_center_id": None,
        "truck_number": None,
        "is_credit_note": False,
        "is_self_pickup": False,
        "is_early_payment": False,
        "reference_invoice_number": None,
        "is_printed": False,
        "is_delivered": False,
        "invoice_number": None,
        "totals": {},
        "created_at": datetime(2026, 6, 13, 0, 0, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 6, 13, 0, 0, tzinfo=timezone.utc),
        "positionen": [],
    }

    class DictMapping(dict):
        pass

    return DictMapping(data)


def _mock_db_for_deliver(dn_mapping):
    db = MagicMock()

    def execute_side(sql, params=None):
        sql_str = str(sql)
        result = MagicMock()
        if "delivery_notes" in sql_str and "SELECT" in sql_str and "delivery_note_positions" not in sql_str:
            result.mappings.return_value.first.return_value = dn_mapping
        elif "delivery_note_positions" in sql_str:
            result.mappings.return_value.all.return_value = []
        else:
            result.fetchone.return_value = None
            result.fetchall.return_value = []
            result.mappings.return_value.all.return_value = []
        return result

    db.execute.side_effect = execute_side
    return db
