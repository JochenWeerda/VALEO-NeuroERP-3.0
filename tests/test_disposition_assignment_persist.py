"""Persistenz der LKW-Zuweisung gegen den gemeinsamen Prüfstand.

Keine neue Datenbank, kein Alembic-Upgrade, kein MagicMock.
Eigene Zeilen werden am Ende gelöscht.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import text

from app.services.disposition_assignment_service import confirm_assignment
from app.services.disposition_assignment_validation import ASSIGNMENT_CONFIRMED_EVENT, AssignmentContext

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]

START = datetime(2026, 10, 22, 6, 0, tzinfo=timezone.utc)
END = datetime(2026, 10, 22, 14, 0, tzinfo=timezone.utc)


def _tables_ready(session) -> bool:
    n = session.execute(
        text(
            "SELECT count(*) FROM information_schema.tables "
            "WHERE table_schema = 'domain_logistics' "
            "AND table_name IN ('tours', 'tour_stops')"
        )
    ).scalar()
    if int(n or 0) < 2:
        return False
    outbox = session.execute(
        text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'outbox_events' LIMIT 1"
        )
    ).scalar()
    return outbox is not None


def _ctx(tenant_id: str, tour_id: str, order_id: str, **overrides: object) -> AssignmentContext:
    data = dict(
        tenant_id=tenant_id,
        actor_tenant_id=tenant_id,
        actor_permissions=frozenset({"logistics.write"}),
        order_id=order_id,
        resource_id=tour_id,
        resource_tenant_id=tenant_id,
        planned_start=START,
        planned_end=END,
        window_start=START,
        window_end=END,
        order_weight_kg=Decimal("1000"),
        assigned_weight_kg=Decimal("0"),
        resource_capacity_kg=Decimal("20000"),
        drop_quantity=Decimal("1"),
        contract_remaining_qty=Decimal("10"),
        allow_overdelivery=False,
        expected_version=None,
        current_version=None,
        approval_required=False,
        approval_granted=False,
        posts_quantity=False,
    )
    data.update(overrides)
    return AssignmentContext(**data)  # type: ignore[arg-type]


def _purge(session, tour_id: str, tenant_id: str) -> None:
    session.execute(text("DELETE FROM domain_logistics.tour_stops WHERE tour_id = :id"), {"id": tour_id})
    session.execute(
        text("DELETE FROM domain_logistics.tours WHERE id = :id AND tenant_id = :tid"),
        {"id": tour_id, "tid": tenant_id},
    )
    session.execute(
        text("DELETE FROM outbox_events WHERE aggregate_id = :id AND tenant_id = :tid"),
        {"id": tour_id, "tid": tenant_id},
    )
    session.commit()


def test_assignment_writes_tour_stop_and_ist_outbox(require_db) -> None:
    from app.core.database import SessionLocal

    session = SessionLocal()
    tenant_id = f"dispo-{uuid.uuid4().hex[:8]}"
    tour_id = str(uuid.uuid4())
    order_id = f"LS-{uuid.uuid4().hex[:8]}"
    try:
        if not _tables_ready(session):
            pytest.skip("domain_logistics.tours/tour_stops oder outbox_events fehlen auf dem Prüfstand")
        result = confirm_assignment(
            _ctx(tenant_id, tour_id, order_id),
            db=session,
            dry_run=False,
        )
        assert result["ok"] is True
        assert result["persisted"] is True
        assert result["quantity_posted"] is False
        assert result["event"] == ASSIGNMENT_CONFIRMED_EVENT
        assert result["event"] == "logistik.tour.created"
        assert result["tour_id"] == tour_id
        assert result["stop_id"]

        tour = session.execute(
            text(
                "SELECT id, tenant_id, status, notes FROM domain_logistics.tours "
                "WHERE id = :id AND tenant_id = :tid"
            ),
            {"id": tour_id, "tid": tenant_id},
        ).mappings().one()
        assert tour["status"] == "GEPLANT"
        assert order_id in str(tour["notes"])

        stop = session.execute(
            text(
                "SELECT delivery_note_ref, tenant_id FROM domain_logistics.tour_stops "
                "WHERE id = :sid AND tour_id = :tid"
            ),
            {"sid": result["stop_id"], "tid": tour_id},
        ).mappings().one()
        assert stop["delivery_note_ref"] == order_id
        assert stop["tenant_id"] == tenant_id

        event = session.execute(
            text(
                "SELECT event_type, payload FROM outbox_events "
                "WHERE id = :eid AND tenant_id = :tid"
            ),
            {"eid": result["outbox_event_id"], "tid": tenant_id},
        ).mappings().one()
        assert event["event_type"] == "logistik.tour.created"
        assert "quantity_posted" in str(event["payload"])
    finally:
        _purge(session, tour_id, tenant_id)
        session.close()


def test_foreign_tenant_tour_is_not_written(require_db) -> None:
    from app.core.database import SessionLocal

    session = SessionLocal()
    owner = f"dispo-a-{uuid.uuid4().hex[:6]}"
    other = f"dispo-b-{uuid.uuid4().hex[:6]}"
    tour_id = str(uuid.uuid4())
    try:
        if not _tables_ready(session):
            pytest.skip("domain_logistics.tours/tour_stops oder outbox_events fehlen auf dem Prüfstand")
        session.execute(
            text(
                "INSERT INTO domain_logistics.tours "
                "(id, date, status, notes, tenant_id) "
                "VALUES (:id, :date, 'GEPLANT', 'seed', :tid)"
            ),
            {"id": tour_id, "date": START, "tid": owner},
        )
        session.commit()
        result = confirm_assignment(
            _ctx(other, tour_id, "LS-fremd", resource_tenant_id=other, actor_tenant_id=other),
            db=session,
            dry_run=False,
        )
        assert result["ok"] is False
        assert result["persisted"] is False
        codes = {issue["code"] for issue in result["issues"]}
        assert "resource_tenant_mismatch" in codes
        stops = session.execute(
            text("SELECT count(*) FROM domain_logistics.tour_stops WHERE tour_id = :id"),
            {"id": tour_id},
        ).scalar()
        assert int(stops or 0) == 0
    finally:
        _purge(session, tour_id, owner)
        session.close()
