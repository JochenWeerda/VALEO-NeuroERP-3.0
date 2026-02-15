"""Personal endpoints for employee list, time entries and timesheets."""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/personal", tags=["personal", "hr"])


class MitarbeiterOut(BaseModel):
    id: str
    name: str
    abteilung: str
    position: str
    eintrittsdatum: str
    status: str


class ZeitEintragOut(BaseModel):
    id: str
    mitarbeiter: str
    datum: str
    kommen: str
    gehen: str
    stunden: float
    typ: str


class TourIn(BaseModel):
    id: str
    start: str
    ende: str
    km: float = 0
    pause: float = 0


class StundenzettelIn(BaseModel):
    datum: str
    fahrer: str
    kennzeichen: str
    touren: list[TourIn] = Field(default_factory=list)
    gesamtArbeitszeit: float = 0
    ueberstunden: float = 0
    unterschrift: str | None = None


def _to_iso(d: date | datetime | None) -> str:
    if d is None:
        return datetime.utcnow().date().isoformat()
    if isinstance(d, datetime):
        return d.date().isoformat()
    return d.isoformat()


def _to_time_text(value: Any) -> str:
    if value is None:
        return "-"
    if hasattr(value, "strftime"):
        return value.strftime("%H:%M")
    text_value = str(value)
    if len(text_value) >= 5:
        return text_value[:5]
    return text_value


@router.get("/mitarbeiter", response_model=list[MitarbeiterOut])
async def list_mitarbeiter(
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    params: dict[str, Any] = {"tenant_id": tenant_id}
    where = ["tenant_id = :tenant_id"]
    if search and search.strip():
        params["needle"] = f"%{search.strip()}%"
        where.append("(username ILIKE :needle OR email ILIKE :needle OR first_name ILIKE :needle OR last_name ILIKE :needle)")
    if status in {"aktiv", "inaktiv"}:
        params["is_active"] = status == "aktiv"
        where.append("is_active = :is_active")

    rows = db.execute(
        text(
            f"""
            SELECT id, username, email, first_name, last_name, roles, is_active, created_at
            FROM domain_shared.users
            WHERE {' AND '.join(where)}
            ORDER BY last_name ASC, first_name ASC, username ASC
            """
        ),
        params,
    ).mappings().all()

    out: list[MitarbeiterOut] = []
    for row in rows:
        roles = row.get("roles") or []
        role_name = "Mitarbeiter"
        if isinstance(roles, list) and roles:
            role_name = str(roles[0])
        first = (row.get("first_name") or "").strip()
        last = (row.get("last_name") or "").strip()
        display = f"{first} {last}".strip() or (row.get("username") or row.get("email") or str(row["id"]))
        out.append(
            MitarbeiterOut(
                id=str(row["id"]),
                name=display,
                abteilung="Allgemein",
                position=role_name,
                eintrittsdatum=_to_iso(row.get("created_at")),
                status="aktiv" if bool(row.get("is_active")) else "krank",
            )
        )

    if status in {"urlaub", "krank"}:
        out = [item for item in out if item.status == status]
    return out


@router.get("/zeiterfassung", response_model=list[ZeitEintragOut])
async def list_zeiterfassung(
    datum: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    params: dict[str, Any] = {"tenant_id": tenant_id}
    where = ["tenant_id = :tenant_id"]
    if datum:
        where.append("entry_date = :entry_date")
        params["entry_date"] = datum

    rows = db.execute(
        text(
            f"""
            SELECT id, employee_ref, entry_date, start_time, end_time, hours, entry_type
            FROM domain_hr.time_entries
            WHERE {' AND '.join(where)}
            ORDER BY entry_date DESC, employee_ref ASC
            """
        ),
        params,
    ).mappings().all()

    return [
        ZeitEintragOut(
            id=str(row["id"]),
            mitarbeiter=str(row.get("employee_ref") or ""),
            datum=_to_iso(row.get("entry_date")),
            kommen=_to_time_text(row.get("start_time")),
            gehen=_to_time_text(row.get("end_time")),
            stunden=float(row.get("hours") or 0),
            typ=str(row.get("entry_type") or "Arbeit"),
        )
        for row in rows
    ]


@router.post("/stundenzettel")
async def create_stundenzettel(
    payload: StundenzettelIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        entry_date = datetime.fromisoformat(payload.datum).date()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid datum format") from exc

    timesheet_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_hr.driver_timesheets
              (id, tenant_id, entry_date, driver_name, vehicle_plate, tours, total_hours, overtime_hours, signature_data, created_at, updated_at)
            VALUES
              (:id, :tenant_id, :entry_date, :driver_name, :vehicle_plate, CAST(:tours AS jsonb), :total_hours, :overtime_hours, :signature_data, NOW(), NOW())
            """
        ),
        {
            "id": timesheet_id,
            "tenant_id": tenant_id,
            "entry_date": entry_date,
            "driver_name": payload.fahrer,
            "vehicle_plate": payload.kennzeichen,
            "tours": json.dumps([tour.model_dump() for tour in payload.touren]),
            "total_hours": payload.gesamtArbeitszeit,
            "overtime_hours": payload.ueberstunden,
            "signature_data": payload.unterschrift,
        },
    )

    start_values = [tour.start for tour in payload.touren if tour.start]
    end_values = [tour.ende for tour in payload.touren if tour.ende]
    start_time = min(start_values) if start_values else None
    end_time = max(end_values) if end_values else None
    entry_type = "Ueberstunden" if payload.ueberstunden > 0 else "Arbeit"

    db.execute(
        text(
            """
            INSERT INTO domain_hr.time_entries
              (id, tenant_id, employee_ref, entry_date, start_time, end_time, hours, entry_type, source, notes, created_at, updated_at)
            VALUES
              (:id, :tenant_id, :employee_ref, :entry_date, :start_time, :end_time, :hours, :entry_type, 'timesheet', :notes, NOW(), NOW())
            """
        ),
        {
            "id": str(uuid4()),
            "tenant_id": tenant_id,
            "employee_ref": payload.fahrer,
            "entry_date": entry_date,
            "start_time": start_time,
            "end_time": end_time,
            "hours": payload.gesamtArbeitszeit,
            "entry_type": entry_type,
            "notes": f"LKW {payload.kennzeichen}",
        },
    )
    db.commit()
    return {"ok": True, "timesheet_id": timesheet_id}
