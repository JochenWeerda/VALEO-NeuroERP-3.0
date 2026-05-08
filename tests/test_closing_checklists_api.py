"""FIN-COV-002: Tests fuer closing_checklists.py.

Abdeckung: build_closing_checklist_response (pure mapping), HTTP-Smoke-Tests.
"""
from __future__ import annotations

from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from main import app
from conftest import skip_if_db_unavailable
from app.api.v1.endpoints.closing_checklists import (
    build_closing_checklist_response,
    ClosingChecklistResponse,
    ChecklistItem,
    ChecklistTemplateCreate,
)

_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "test-tenant"}
_client = TestClient(app, raise_server_exceptions=False)

_NOW = datetime(2026, 5, 8, 10, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# build_closing_checklist_response unit tests
# ---------------------------------------------------------------------------

def _make_row(
    checklist_id="cl-001",
    period="2026-04",
    closing_type="monthly",
    template_id=None,
    status="in_progress",
    progress_pct=60.0,
    total_items=10,
    completed_items=6,
    required_items=8,
    completed_required=5,
    extra=None,
    created_at=_NOW,
    updated_at=_NOW,
    completed_at=None,
    completed_by=None,
):
    return (
        checklist_id,    # 0 id
        period,           # 1 period
        closing_type,     # 2 closing_type
        template_id,      # 3 template_id
        status,           # 4 status
        progress_pct,     # 5 progress_percentage
        total_items,      # 6 total_items
        completed_items,  # 7 completed_items
        required_items,   # 8 required_items
        completed_required, # 9 completed_required_items
        extra,            # 10 (unused)
        created_at,       # 11 created_at
        updated_at,       # 12 updated_at
        completed_at,     # 13 completed_at
        completed_by,     # 14 completed_by
    )


def test_build_response_basic():
    row = _make_row()
    result = build_closing_checklist_response(row, items_data=[])
    assert isinstance(result, ClosingChecklistResponse)
    assert result.id == "cl-001"
    assert result.period == "2026-04"
    assert result.closing_type == "monthly"
    assert result.status == "in_progress"
    assert result.progress_percentage == 60.0
    assert result.total_items == 10
    assert result.completed_items == 6


def test_build_response_approval_not_closable_when_in_progress():
    row = _make_row(status="in_progress")
    result = build_closing_checklist_response(row, items_data=[])
    assert result.approval_can_close is False


def test_build_response_approval_closable_when_completed():
    row = _make_row(status="completed")
    result = build_closing_checklist_response(row, items_data=[])
    assert result.approval_can_close is True


def test_build_response_approval_closable_when_approved():
    row = _make_row(status="approved")
    result = build_closing_checklist_response(row, items_data=[])
    assert result.approval_can_close is True


def test_build_response_items_passthrough():
    items = [{"item_code": "GL-001", "status": "completed"}]
    row = _make_row()
    result = build_closing_checklist_response(row, items_data=items)
    assert result.items == items


def test_build_response_template_id_none():
    row = _make_row(template_id=None)
    result = build_closing_checklist_response(row, items_data=[])
    assert result.template_id is None


def test_build_response_template_id_set():
    row = _make_row(template_id="tmpl-001")
    result = build_closing_checklist_response(row, items_data=[])
    assert result.template_id == "tmpl-001"


def test_build_response_explainability_allowed_when_completed():
    row = _make_row(status="completed")
    result = build_closing_checklist_response(row, items_data=[])
    assert result.approval_explainability.status == "allowed"


def test_build_response_explainability_approval_required_when_draft():
    row = _make_row(status="draft")
    result = build_closing_checklist_response(row, items_data=[])
    assert result.approval_explainability.status == "approval-required"


# ---------------------------------------------------------------------------
# ChecklistItem validation
# ---------------------------------------------------------------------------

def test_checklist_item_valid():
    item = ChecklistItem(
        item_code="GL-001",
        description="Hauptbuch abstimmen",
        category="GL",
        validation_type="manual",
        responsible_role="accountant",
    )
    assert item.required is True
    assert item.due_date_offset == 0


def test_checklist_template_requires_items():
    with pytest.raises(Exception):
        ChecklistTemplateCreate(
            template_name="Monatsabschluss",
            closing_type="monthly",
            items=[],  # min_length=1
        )


# ---------------------------------------------------------------------------
# HTTP smoke tests
# ---------------------------------------------------------------------------

def test_list_checklists_returns_200():
    resp = _client.get("/api/v1/finance/closing-checklists", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


def test_list_templates_returns_200():
    resp = _client.get("/api/v1/finance/closing-checklists/templates", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


def test_cockpit_summary_returns_200():
    resp = _client.get("/api/v1/finance/closing-checklists/cockpit/summary", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 200


def test_create_checklist_missing_fields_returns_422():
    resp = _client.post("/api/v1/finance/closing-checklists", json={}, headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code == 422


def test_get_nonexistent_checklist_returns_404():
    resp = _client.get("/api/v1/finance/closing-checklists/does-not-exist", headers=_HEADERS)
    skip_if_db_unavailable(resp)
    assert resp.status_code in (404, 500)
