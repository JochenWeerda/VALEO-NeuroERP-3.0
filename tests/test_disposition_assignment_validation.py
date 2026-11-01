"""Reine Zuweisungsprüfung für LKW-Disposition — ohne Datenbank, ohne MagicMock."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.services.disposition_assignment_repository import stop_insert_params, tour_insert_params
from app.services.disposition_assignment_service import confirm_assignment
from app.services.disposition_assignment_validation import (
    ASSIGNMENT_CONFIRMED_EVENT,
    QUANTITY_POSTED_EVENT,
    AssignmentContext,
    permissions_from_roles,
    quantity_posted_is_separate_event,
    validate_assignment,
)

pytestmark = pytest.mark.unit

START = datetime(2026, 10, 22, 6, 0, tzinfo=timezone.utc)
END = datetime(2026, 10, 22, 14, 0, tzinfo=timezone.utc)


def _ctx(**overrides: object) -> AssignmentContext:
    data = dict(
        tenant_id="haus-a",
        actor_tenant_id="haus-a",
        actor_permissions=frozenset({"logistics.write", "logistics.read"}),
        order_id="ord-1",
        resource_id="tour-1",
        resource_tenant_id="haus-a",
        planned_start=START,
        planned_end=END,
        window_start=START,
        window_end=END,
        order_weight_kg=Decimal("8000"),
        assigned_weight_kg=Decimal("5000"),
        resource_capacity_kg=Decimal("20000"),
        drop_quantity=Decimal("10"),
        contract_remaining_qty=Decimal("25"),
        allow_overdelivery=False,
        expected_version=3,
        current_version=3,
        approval_required=False,
        approval_granted=False,
        posts_quantity=False,
    )
    data.update(overrides)
    return AssignmentContext(**data)  # type: ignore[arg-type]


def _codes(ctx: AssignmentContext) -> set[str]:
    return {issue.code for issue in validate_assignment(ctx).issues}


def test_happy_path_emits_assignment_confirmed_not_quantity_posted() -> None:
    decision = validate_assignment(_ctx())
    assert decision.ok is True
    assert decision.persist_allowed is True
    assert decision.event == ASSIGNMENT_CONFIRMED_EVENT
    assert decision.event == "logistik.tour.created"
    assert decision.event != QUANTITY_POSTED_EVENT
    assert decision.event != "assignment_confirmed"
    assert quantity_posted_is_separate_event() == QUANTITY_POSTED_EVENT


def test_drop_must_not_post_contract_quantity() -> None:
    decision = validate_assignment(_ctx(posts_quantity=True))
    assert decision.ok is False
    assert "quantity_post_on_drop_forbidden" in _codes(_ctx(posts_quantity=True))
    assert decision.event is None


def test_tenant_and_permission_are_blocking() -> None:
    assert "tenant_mismatch" in _codes(_ctx(actor_tenant_id="anderes-haus"))
    assert "resource_tenant_mismatch" in _codes(_ctx(resource_tenant_id="anderes-haus"))
    assert "missing_permission" in _codes(_ctx(actor_permissions=frozenset({"logistics.read"})))


def test_capacity_and_time_window() -> None:
    assert "capacity_exceeded" in _codes(_ctx(order_weight_kg=Decimal("16000")))
    too_late = datetime(2026, 10, 22, 18, 0, tzinfo=timezone.utc)
    assert "time_window_violation" in _codes(_ctx(planned_end=too_late))
    assert "invalid_time_range" in _codes(_ctx(planned_end=START))


def test_contract_quantity_and_concurrency_and_approval() -> None:
    assert "contract_quantity_exceeded" in _codes(_ctx(drop_quantity=Decimal("40")))
    allowed = validate_assignment(_ctx(drop_quantity=Decimal("40"), allow_overdelivery=True))
    assert allowed.ok is True
    assert "concurrent_change" in _codes(_ctx(expected_version=3, current_version=4))
    assert "approval_required" in _codes(_ctx(approval_required=True, approval_granted=False))
    approved = validate_assignment(_ctx(approval_required=True, approval_granted=True))
    assert approved.ok is True


def test_permissions_come_from_roles_not_from_client_payload() -> None:
    assert "logistics.write" in permissions_from_roles(["Disponent"])
    assert "logistics.write" not in permissions_from_roles(["logistics.read"])
    assert permissions_from_roles([]) == frozenset()


def test_confirm_assignment_dry_run_does_not_persist() -> None:
    result = confirm_assignment(_ctx(), db=None, dry_run=True)
    assert result["ok"] is True
    assert result["persisted"] is False
    assert result["quantity_posted"] is False
    assert result["event"] == ASSIGNMENT_CONFIRMED_EVENT
    assert result["tour_id"] is None


def test_insert_params_match_logistics_core_migration() -> None:
    tour = tour_insert_params(
        tour_id="tour-1",
        tenant_id="haus-a",
        planned_start=START,
        order_id="ord-1",
    )
    stop = stop_insert_params(
        stop_id="stop-1",
        tour_id="tour-1",
        tenant_id="haus-a",
        order_id="ord-1",
        stop_order=0,
        planned_arrival=START,
    )
    assert set(tour) == {"id", "date", "vehicle_id", "driver_id", "status", "notes", "tenant_id"}
    assert tour["status"] == "GEPLANT"
    assert set(stop) == {
        "id", "tour_id", "stop_order", "address", "lat", "lng", "customer_id",
        "delivery_note_ref", "planned_arrival", "status", "tenant_id",
    }
    assert stop["delivery_note_ref"] == "ord-1"
    assert "qty" not in stop and "menge" not in stop
    tour_abruf = tour_insert_params(
        tour_id="tour-1",
        tenant_id="haus-a",
        planned_start=START,
        order_id="ord-1",
        abruf_id="abruf-9",
    )
    assert tour_abruf["notes"] == "disposition:ord-1;abruf:abruf-9"
    assert set(tour_abruf) == set(tour)


def test_confirm_assignment_echoes_optional_abruf_id() -> None:
    result = confirm_assignment(_ctx(abruf_id="abruf-9"), db=None, dry_run=True)
    assert result["ok"] is True
    assert result["abruf_id"] == "abruf-9"
    assert result["quantity_posted"] is False
