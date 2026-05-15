"""Unit tests for DocflowService."""
from decimal import Decimal
from unittest.mock import MagicMock
from datetime import datetime
import json
import pytest
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.services.docflow_service import (
    DocflowService, TRANSITIONS, DOC_PREFIX, POS_TYPES,
    _money, _qty, _line_amounts,
)

def _make_svc(tenant_id="t1"):
    db = MagicMock()
    return DocflowService(db, tenant_id), db

def test_money_rounds_half_up():
    assert _money(Decimal("2.555")) == Decimal("2.56")
    assert _money(Decimal("2.554")) == Decimal("2.55")

def test_qty_three_decimals():
    assert _qty(Decimal("1.2345")) == Decimal("1.235")

def test_line_amounts_no_discount():
    net, tax, gross = _line_amounts(Decimal("2"), Decimal("100"), Decimal("0"), Decimal("19"))
    assert net == Decimal("200.00")
    assert tax == Decimal("38.00")
    assert gross == Decimal("238.00")

def test_line_amounts_with_discount():
    net, tax, gross = _line_amounts(Decimal("1"), Decimal("100"), Decimal("10"), Decimal("19"))
    assert net == Decimal("90.00")

def test_transitions_sales_order_targets():
    assert "sales_delivery" in TRANSITIONS["sales_order"]
    assert "sales_invoice" in TRANSITIONS["sales_order"]

def test_transitions_invoice_credit_memo():
    assert "sales_credit_memo" in TRANSITIONS["sales_invoice"]

def test_pos_types_subset_of_doc_types():
    # pos_storno is a target only, not a source — check POS_TYPES overlap
    all_types = set(TRANSITIONS.keys()) | {t for targets in TRANSITIONS.values() for t in targets}
    for pt in POS_TYPES:
        assert pt in all_types

def test_allocate_doc_number_prefix():
    svc, db = _make_svc()
    # No existing row -> INSERT path; counter starts at 1
    db.execute.return_value.mappings.return_value.first.return_value = None
    num = svc.allocate_doc_number("sales_order", datetime(2025, 5, 15))
    assert num.startswith("SOR")

def test_load_create_idempotency_none():
    svc, db = _make_svc()
    db.execute.return_value.mappings.return_value.first.return_value = None
    assert svc.load_create_idempotency("k1") is None

def test_load_create_idempotency_hit():
    svc, db = _make_svc()
    db.execute.return_value.mappings.return_value.first.return_value = {"doc_id": "doc-1"}
    assert svc.load_create_idempotency("k1") == "doc-1"

def test_store_create_idempotency_executes():
    svc, db = _make_svc()
    svc.store_create_idempotency("k1", "doc-1")
    db.execute.assert_called_once()

def test_load_idempotent_response_none():
    svc, db = _make_svc()
    db.execute.return_value.mappings.return_value.first.return_value = None
    assert svc.load_idempotent_response("release", "d1", "k1") is None

def test_load_idempotent_response_deserialises():
    svc, db = _make_svc()
    db.execute.return_value.mappings.return_value.first.return_value = {"response_payload": {"status": "ok"}}
    assert svc.load_idempotent_response("release", "d1", "k1") == {"status": "ok"}

def test_upsert_outbox_event_is_string():
    svc, db = _make_svc()
    event_id = svc.upsert_outbox_event("doc.released", "doc-1", {"x": 1})
    assert isinstance(event_id, str) and len(event_id) > 0
    # Just verify format
    assert "-" in event_id

def test_fetch_header_none():
    svc, db = _make_svc()
    db.execute.return_value.mappings.return_value.first.return_value = None
    assert svc.fetch_header("doc-99") is None

def test_fetch_header_returns_dict():
    svc, db = _make_svc()
    row = {"id": "d1", "doc_type": "sales_order", "status": "draft"}
    db.execute.return_value.mappings.return_value.first.return_value = row
    assert svc.fetch_header("d1")["doc_type"] == "sales_order"

def test_fetch_items_returns_list():
    svc, db = _make_svc()
    db.execute.return_value.mappings.return_value.all.return_value = [{"id": "i1"}]
    assert len(svc.fetch_items("d1")) == 1

def test_release_raises_not_found():
    svc, db = _make_svc()
    # load_idempotent_response -> None, fetch_header -> None
    db.execute.return_value.mappings.return_value.first.side_effect = [None, None]
    with pytest.raises(EntityNotFoundError):
        svc.release("d99", "k1", None, "u1")

def test_release_raises_conflict_version():
    svc, db = _make_svc()
    row = {"id": "d1", "doc_type": "sales_order", "status": "draft", "version": 3, "tenant_id": "t1"}
    # load_idempotent_response -> None, fetch_header -> row with version=3
    db.execute.return_value.mappings.return_value.first.side_effect = [None, row]
    with pytest.raises(ConflictError):
        svc.release("d1", "k1", expected_version=1, released_by="u1")

def test_release_raises_not_draft():
    svc, db = _make_svc()
    row = {"id": "d1", "doc_type": "sales_order", "status": "released", "version": 1, "tenant_id": "t1"}
    # load_idempotent_response -> None, fetch_header -> row with wrong status
    db.execute.return_value.mappings.return_value.first.side_effect = [None, row]
    with pytest.raises(ValidationFailedError):
        svc.release("d1", "k1", expected_version=1, released_by="u1")
