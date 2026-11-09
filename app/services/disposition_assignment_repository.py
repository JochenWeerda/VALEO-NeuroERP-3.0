"""Additives Schreiben der LKW-Zuweisung auf domain_logistics.

Schema ausschließlich aus Alembic ``log_logistics_core_20260612``:
``tours(id, date, vehicle_id, driver_id, status, notes, tenant_id, created_at)``
``tour_stops(id, tour_id, stop_order, address, lat, lng, customer_id,
delivery_note_ref, planned_arrival, actual_arrival, status, pod_data,
tenant_id, created_at)``.

Kein Edit an logistics_tours.py. Keine Mengenbuchung.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.disposition_assignment_validation import AssignmentContext

TOURS_TABLE = "domain_logistics.tours"
STOPS_TABLE = "domain_logistics.tour_stops"


class AssignmentPersistError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class AssignmentPersistResult:
    tour_id: str
    stop_id: str
    created_tour: bool
    stop_order: int


def tour_insert_params(
    *,
    tour_id: str,
    tenant_id: str,
    planned_start: datetime,
    order_id: str,
    vehicle_id: str | None = None,
    driver_id: str | None = None,
    abruf_id: str | None = None,
) -> dict[str, Any]:
    """Parameter für INSERT tours — Spalten nur aus der Kern-Migration."""
    notes = f"disposition:{order_id}"
    if abruf_id:
        notes = f"{notes};abruf:{abruf_id}"
    return {
        "id": tour_id,
        "date": planned_start,
        "vehicle_id": vehicle_id,
        "driver_id": driver_id,
        "status": "GEPLANT",
        "notes": notes,
        "tenant_id": tenant_id,
    }


def stop_insert_params(
    *,
    stop_id: str,
    tour_id: str,
    tenant_id: str,
    order_id: str,
    stop_order: int,
    planned_arrival: datetime,
) -> dict[str, Any]:
    """Parameter für INSERT tour_stops — Spalten nur aus der Kern-Migration."""
    return {
        "id": stop_id,
        "tour_id": tour_id,
        "stop_order": stop_order,
        "address": None,
        "lat": None,
        "lng": None,
        "customer_id": None,
        "delivery_note_ref": order_id,
        "planned_arrival": planned_arrival,
        "status": "GEPLANT",
        "tenant_id": tenant_id,
    }


def load_tour(db: Session, tour_id: str, tenant_id: str) -> dict[str, Any] | None:
    row = db.execute(
        text(
            f"SELECT id, tenant_id, vehicle_id, driver_id, status "
            f"FROM {TOURS_TABLE} WHERE id = :id"  # nosec B608
        ),
        {"id": tour_id},
    ).mappings().first()
    if row is None:
        return None
    payload = dict(row)
    if str(payload.get("tenant_id") or "") != tenant_id:
        raise AssignmentPersistError(
            "resource_tenant_mismatch",
            "Die Ressource gehört zu einem anderen Mandanten.",
        )
    return payload


def count_stops(db: Session, tour_id: str) -> int:
    value = db.execute(
        text(f"SELECT COUNT(*) FROM {STOPS_TABLE} WHERE tour_id = :tid"),  # nosec B608
        {"tid": tour_id},
    ).scalar()
    return int(value or 0)


def persist_assignment(db: Session, ctx: AssignmentContext) -> AssignmentPersistResult:
    """Schreibt Tour und Stopp in derselben Transaktion wie der Aufrufer."""
    existing = load_tour(db, ctx.resource_id, ctx.tenant_id)
    created_tour = existing is None
    tour_id = ctx.resource_id
    stop_order = 0

    if existing is None:
        if ctx.expected_version not in (None, 0) or ctx.current_version not in (None, 0):
            raise AssignmentPersistError(
                "concurrent_change",
                "Die Ressource wurde inzwischen geändert. Bitte neu laden.",
            )
        db.execute(
            text(
                f"""
                INSERT INTO {TOURS_TABLE}
                    (id, date, vehicle_id, driver_id, status, notes, tenant_id)
                VALUES (:id, :date, :vehicle_id, :driver_id, :status, :notes, :tenant_id)
                """  # nosec B608
            ),
            tour_insert_params(
                tour_id=tour_id,
                tenant_id=ctx.tenant_id,
                planned_start=ctx.planned_start,
                order_id=ctx.order_id,
                abruf_id=ctx.abruf_id,
            ),
        )
    else:
        stop_order = count_stops(db, tour_id)
        if ctx.expected_version is not None and ctx.current_version is not None:
            if stop_order != ctx.current_version:
                raise AssignmentPersistError(
                    "concurrent_change",
                    "Die Ressource wurde inzwischen geändert. Bitte neu laden.",
                )

    stop_id = str(uuid.uuid4())
    db.execute(
        text(
            f"""
            INSERT INTO {STOPS_TABLE}
                (id, tour_id, stop_order, address, lat, lng, customer_id,
                 delivery_note_ref, planned_arrival, status, tenant_id)
            VALUES (:id, :tour_id, :stop_order, :address, :lat, :lng,
                    :customer_id, :delivery_note_ref, :planned_arrival, :status, :tenant_id)
            """  # nosec B608
        ),
        stop_insert_params(
            stop_id=stop_id,
            tour_id=tour_id,
            tenant_id=ctx.tenant_id,
            order_id=ctx.order_id,
            stop_order=stop_order,
            planned_arrival=ctx.planned_start,
        ),
    )
    return AssignmentPersistResult(
        tour_id=tour_id,
        stop_id=stop_id,
        created_tour=created_tour,
        stop_order=stop_order,
    )
