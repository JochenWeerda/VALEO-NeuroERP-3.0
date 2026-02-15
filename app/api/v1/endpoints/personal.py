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
    email: str
    abteilung: str
    position: str
    eintrittsdatum: str
    status: str


class MitarbeiterIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: str = Field(..., min_length=3, max_length=120)
    abteilung: str = Field(default="Allgemein", max_length=120)
    position: str = Field(default="Mitarbeiter", max_length=120)
    status: str = Field(default="aktiv", pattern="^(aktiv|urlaub|krank)$")


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


class StundenzettelOut(BaseModel):
    id: str
    datum: str
    fahrer: str
    kennzeichen: str
    touren: list[dict[str, Any]]
    gesamtArbeitszeit: float
    ueberstunden: float
    erstelltAm: str


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


def _normalize_status(value: Any, fallback: str = "aktiv") -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"aktiv", "urlaub", "krank"}:
        return normalized
    return fallback


def _parse_preferences(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return {}
    return {}


def _split_name(full_name: str) -> tuple[str, str]:
    parts = [part for part in full_name.strip().split(" ") if part]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return " ".join(parts[:-1]), parts[-1]


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
            SELECT id, username, email, first_name, last_name, roles, is_active, preferences, created_at
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
        prefs = _parse_preferences(row.get("preferences"))
        hr_status = _normalize_status(prefs.get("hr_status"), "aktiv" if bool(row.get("is_active")) else "krank")
        abteilung = str(prefs.get("abteilung") or "Allgemein")
        first = (row.get("first_name") or "").strip()
        last = (row.get("last_name") or "").strip()
        display = f"{first} {last}".strip() or (row.get("username") or row.get("email") or str(row["id"]))
        out.append(
            MitarbeiterOut(
                id=str(row["id"]),
                name=display,
                email=str(row.get("email") or ""),
                abteilung=abteilung,
                position=role_name,
                eintrittsdatum=_to_iso(row.get("created_at")),
                status=hr_status,
            )
        )

    if status in {"aktiv", "urlaub", "krank"}:
        out = [item for item in out if item.status == status]
    return out


@router.get("/mitarbeiter/{user_id}", response_model=MitarbeiterOut)
async def get_mitarbeiter(
    user_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = db.execute(
        text(
            """
            SELECT id, username, email, first_name, last_name, roles, is_active, preferences, created_at
            FROM domain_shared.users
            WHERE id = :user_id AND tenant_id = :tenant_id
            """
        ),
        {"user_id": user_id, "tenant_id": tenant_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Mitarbeiter nicht gefunden")
    roles = row.get("roles") or []
    role_name = "Mitarbeiter"
    if isinstance(roles, list) and roles:
        role_name = str(roles[0])
    prefs = _parse_preferences(row.get("preferences"))
    hr_status = _normalize_status(prefs.get("hr_status"), "aktiv" if bool(row.get("is_active")) else "krank")
    abteilung = str(prefs.get("abteilung") or "Allgemein")
    first = (row.get("first_name") or "").strip()
    last = (row.get("last_name") or "").strip()
    display = f"{first} {last}".strip() or (row.get("username") or row.get("email") or str(row["id"]))
    return MitarbeiterOut(
        id=str(row["id"]),
        name=display,
        email=str(row.get("email") or ""),
        abteilung=abteilung,
        position=role_name,
        eintrittsdatum=_to_iso(row.get("created_at")),
        status=hr_status,
    )


@router.post("/mitarbeiter", response_model=MitarbeiterOut, status_code=201)
async def create_mitarbeiter(
    payload: MitarbeiterIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    existing = db.execute(
        text(
            """
            SELECT 1
            FROM domain_shared.users
            WHERE tenant_id = :tenant_id AND (email = :email OR username = :username)
            LIMIT 1
            """
        ),
        {"tenant_id": tenant_id, "email": payload.email, "username": payload.email},
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Mitarbeiter mit E-Mail existiert bereits")

    first_name, last_name = _split_name(payload.name)
    user_id = str(uuid4())
    role_slug = payload.position.strip().lower().replace(" ", "_")
    if not role_slug:
        role_slug = "mitarbeiter"
    db.execute(
        text(
            """
            INSERT INTO domain_shared.users
              (id, keycloak_id, username, email, first_name, last_name, is_active, roles, tenant_id, preferences, created_at, updated_at)
            VALUES
              (:id, :keycloak_id, :username, :email, :first_name, :last_name, :is_active, :roles, :tenant_id, CAST(:preferences AS jsonb), NOW(), NOW())
            """
        ),
        {
            "id": user_id,
            "keycloak_id": f"local-{user_id}",
            "username": payload.email,
            "email": payload.email,
            "first_name": first_name,
            "last_name": last_name,
            "is_active": payload.status != "krank",
            "roles": [role_slug],
            "tenant_id": tenant_id,
            "preferences": json.dumps({"hr_status": payload.status, "abteilung": payload.abteilung}),
        },
    )
    db.commit()
    return await get_mitarbeiter(user_id=user_id, tenant_id=tenant_id, db=db)


@router.put("/mitarbeiter/{user_id}", response_model=MitarbeiterOut)
async def update_mitarbeiter(
    user_id: str,
    payload: MitarbeiterIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    first_name, last_name = _split_name(payload.name)
    role_slug = payload.position.strip().lower().replace(" ", "_")
    if not role_slug:
        role_slug = "mitarbeiter"
    updated = db.execute(
        text(
            """
            UPDATE domain_shared.users
            SET email = :email,
                username = :username,
                first_name = :first_name,
                last_name = :last_name,
                is_active = :is_active,
                roles = :roles,
                preferences = COALESCE(preferences, '{}'::jsonb) || CAST(:preferences AS jsonb),
                updated_at = NOW()
            WHERE id = :user_id AND tenant_id = :tenant_id
            """
        ),
        {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "email": payload.email,
            "username": payload.email,
            "first_name": first_name,
            "last_name": last_name,
            "is_active": payload.status != "krank",
            "roles": [role_slug],
            "preferences": json.dumps({"hr_status": payload.status, "abteilung": payload.abteilung}),
        },
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Mitarbeiter nicht gefunden")
    db.commit()
    return await get_mitarbeiter(user_id=user_id, tenant_id=tenant_id, db=db)


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


@router.get("/stundenzettel", response_model=list[StundenzettelOut])
async def list_stundenzettel(
    datum_von: str | None = Query(default=None),
    datum_bis: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    params: dict[str, Any] = {"tenant_id": tenant_id}
    where = ["tenant_id = :tenant_id"]
    if datum_von:
        where.append("entry_date >= :datum_von")
        params["datum_von"] = datum_von
    if datum_bis:
        where.append("entry_date <= :datum_bis")
        params["datum_bis"] = datum_bis

    rows = db.execute(
        text(
            f"""
            SELECT id, entry_date, driver_name, vehicle_plate, tours, total_hours, overtime_hours, created_at
            FROM domain_hr.driver_timesheets
            WHERE {' AND '.join(where)}
            ORDER BY entry_date DESC, created_at DESC
            """
        ),
        params,
    ).mappings().all()

    out: list[StundenzettelOut] = []
    for row in rows:
        tours_raw = row.get("tours")
        tours: list[dict[str, Any]]
        if isinstance(tours_raw, list):
            tours = [dict(item) if isinstance(item, dict) else {"value": item} for item in tours_raw]
        elif isinstance(tours_raw, str):
            try:
                parsed = json.loads(tours_raw)
                if isinstance(parsed, list):
                    tours = [dict(item) if isinstance(item, dict) else {"value": item} for item in parsed]
                else:
                    tours = []
            except Exception:
                tours = []
        else:
            tours = []

        out.append(
            StundenzettelOut(
                id=str(row["id"]),
                datum=_to_iso(row.get("entry_date")),
                fahrer=str(row.get("driver_name") or ""),
                kennzeichen=str(row.get("vehicle_plate") or ""),
                touren=tours,
                gesamtArbeitszeit=float(row.get("total_hours") or 0),
                ueberstunden=float(row.get("overtime_hours") or 0),
                erstelltAm=_to_iso(row.get("created_at")),
            )
        )
    return out
