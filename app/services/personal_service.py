"""Service layer for HR/Personal domain queries (Mitarbeiter, Zeiterfassung, Abwesenheiten)."""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any, List, Optional, Sequence

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError
from app.core.uuid7 import uuid7

logger = logging.getLogger(__name__)

# ── pure value helpers (no DB, no side-effects) ───────────────────────────────

def normalize_status(value: Any, fallback: str = "aktiv") -> str:
    if not value:
        return fallback
    s = str(value).strip().lower()
    return s if s in {"aktiv", "urlaub", "krank", "inaktiv"} else fallback


def parse_preferences(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        import json
        try:
            return json.loads(raw)
        except Exception:
            return {}
    return {}


def parse_json_list(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, list):
        return raw
    if isinstance(raw, str):
        import json
        try:
            result = json.loads(raw)
            return result if isinstance(result, list) else []
        except Exception:
            return []
    return []


def parse_json_string_list(raw: Any) -> list[str]:
    items = parse_json_list(raw)
    return [str(x) for x in items]


def to_iso(d: date | datetime | None) -> str:
    if d is None:
        return ""
    if isinstance(d, datetime):
        return d.date().isoformat()
    return d.isoformat()


def split_name(full_name: str) -> tuple[str, str]:
    parts = full_name.strip().split(" ", 1)
    return (parts[0], parts[1]) if len(parts) == 2 else (full_name, "")


def display_name_from_row(row: Any) -> str:
    first = (row.get("first_name") or "").strip()
    last = (row.get("last_name") or "").strip()
    return f"{first} {last}".strip() or (row.get("username") or row.get("email") or str(row.get("id", "")))


def role_label_from_row(row: Any) -> str:
    roles = row.get("roles") or []
    if isinstance(roles, list) and roles:
        return str(roles[0])
    return "Mitarbeiter"


class PersonalService:
    """Encapsulates all HR/Personal DB queries with fallback strategy."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── Mitarbeiter ───────────────────────────────────────────────────────────

    def list_mitarbeiter(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[dict]:
        params: dict[str, Any] = {"tenant_id": self.tenant_id}
        where = ["tenant_id = :tenant_id"]
        if search and search.strip():
            params["needle"] = f"%{search.strip()}%"
            where.append("(username ILIKE :needle OR email ILIKE :needle OR first_name ILIKE :needle OR last_name ILIKE :needle)")
        if status in {"aktiv", "inaktiv"}:
            params["is_active"] = status == "aktiv"
            where.append("is_active = :is_active")

        rows = self.db.execute(
            text(
                f"SELECT id, username, email, first_name, last_name, roles, is_active, preferences, created_at "
                f"FROM domain_shared.users WHERE {' AND '.join(where)} "
                f"ORDER BY last_name ASC, first_name ASC, username ASC"
            ),
            params,
        ).mappings().all()

        result = []
        for row in rows:
            prefs = parse_preferences(row.get("preferences"))
            hr_status = normalize_status(prefs.get("hr_status"), "aktiv" if bool(row.get("is_active")) else "krank")
            result.append({
                "id": str(row["id"]),
                "name": display_name_from_row(row),
                "email": str(row.get("email") or ""),
                "abteilung": str(prefs.get("abteilung") or "Allgemein"),
                "position": role_label_from_row(row),
                "eintrittsdatum": to_iso(row.get("created_at")),
                "status": hr_status,
            })

        if status in {"aktiv", "urlaub", "krank"}:
            result = [m for m in result if m["status"] == status]
        return result

    def get_mitarbeiter(self, user_id: str) -> dict:
        row = self.db.execute(
            text(
                "SELECT id, username, email, first_name, last_name, roles, is_active, preferences, created_at "
                "FROM domain_shared.users WHERE id = :user_id AND tenant_id = :tenant_id"
            ),
            {"user_id": user_id, "tenant_id": self.tenant_id},
        ).mappings().first()
        if not row:
            raise EntityNotFoundError("Mitarbeiter", user_id)
        prefs = parse_preferences(row.get("preferences"))
        hr_status = normalize_status(prefs.get("hr_status"), "aktiv" if bool(row.get("is_active")) else "krank")
        return {
            "id": str(row["id"]),
            "name": display_name_from_row(row),
            "email": str(row.get("email") or ""),
            "abteilung": str(prefs.get("abteilung") or "Allgemein"),
            "position": role_label_from_row(row),
            "eintrittsdatum": to_iso(row.get("created_at")),
            "status": hr_status,
        }

    # ── Zeiteinträge ──────────────────────────────────────────────────────────

    def list_zeiteintraege(
        self,
        mitarbeiter: Optional[str] = None,
        datum_von: Optional[str] = None,
        datum_bis: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[dict]:
        params: dict[str, Any] = {"tenant_id": self.tenant_id}
        where = ["tenant_id = :tenant_id"]
        if mitarbeiter:
            params["mitarbeiter"] = mitarbeiter
            where.append("employee_ref = :mitarbeiter")
        if datum_von:
            params["datum_von"] = datum_von
            where.append("work_date >= :datum_von")
        if datum_bis:
            params["datum_bis"] = datum_bis
            where.append("work_date <= :datum_bis")

        try:
            rows = self.db.execute(
                text(
                    f"SELECT id, employee_ref, work_date, start_time, end_time, total_hours, entry_type, status, "
                    f"cost_center, work_area, correction_reason, approved_by, approved_at, audit_ref "
                    f"FROM domain_hr.time_bookings WHERE {' AND '.join(where)} "
                    f"ORDER BY work_date DESC, start_time ASC LIMIT :limit OFFSET :skip"
                ),
                {**params, "limit": limit, "skip": skip},
            ).mappings().all()
            return [self._time_booking_to_dict(r) for r in rows]
        except Exception:
            logger.debug("time_bookings table not available", exc_info=True)
            return []

    def get_zeiteintrag(self, entry_id: str) -> dict:
        try:
            row = self.db.execute(
                text(
                    "SELECT id, employee_ref, work_date, start_time, end_time, total_hours, entry_type, status, "
                    "cost_center, work_area, correction_reason, approved_by, approved_at, audit_ref "
                    "FROM domain_hr.time_bookings WHERE id = :id AND tenant_id = :tenant_id"
                ),
                {"id": entry_id, "tenant_id": self.tenant_id},
            ).mappings().first()
        except Exception:
            row = None
        if not row:
            raise EntityNotFoundError("Zeiteintrag", entry_id)
        return self._time_booking_to_dict(row)

    def create_zeiteintrag(self, payload: dict) -> dict:
        entry_id = uuid7()
        try:
            self.db.execute(
                text(
                    "INSERT INTO domain_hr.time_bookings "
                    "(id, tenant_id, employee_ref, work_date, start_time, end_time, total_hours, "
                    "entry_type, source, status, cost_center, work_area, notes) "
                    "VALUES (:id, :tenant_id, :employee_ref, :work_date, :start_time, :end_time, "
                    ":total_hours, :entry_type, :source, 'pending', :cost_center, :work_area, :notes)"
                ),
                {
                    "id": entry_id,
                    "tenant_id": self.tenant_id,
                    "employee_ref": payload["employeeRef"],
                    "work_date": payload["datum"],
                    "start_time": payload.get("startTime"),
                    "end_time": payload.get("endTime"),
                    "total_hours": payload["hours"],
                    "entry_type": payload.get("entryType", "Arbeit"),
                    "source": payload.get("source", "manual"),
                    "cost_center": payload.get("costCenter"),
                    "work_area": payload.get("workArea"),
                    "notes": payload.get("notes"),
                },
            )
            self.db.commit()
            return self.get_zeiteintrag(entry_id)
        except Exception as exc:
            self.db.rollback()
            raise ValidationError(str(exc)) from exc  # noqa: F821

    def correct_zeiteintrag(self, entry_id: str, payload: dict) -> dict:
        self.get_zeiteintrag(entry_id)  # raises if not found
        try:
            self.db.execute(
                text(
                    "UPDATE domain_hr.time_bookings SET "
                    "total_hours = :hours, correction_reason = :reason, "
                    "start_time = COALESCE(:start_time, start_time), end_time = COALESCE(:end_time, end_time), "
                    "entry_type = :entry_type, cost_center = COALESCE(:cost_center, cost_center), "
                    "work_area = COALESCE(:work_area, work_area), notes = COALESCE(:notes, notes), "
                    "status = 'corrected' "
                    "WHERE id = :id AND tenant_id = :tenant_id"
                ),
                {
                    "id": entry_id,
                    "tenant_id": self.tenant_id,
                    "hours": payload["hours"],
                    "reason": payload["correctionReason"],
                    "start_time": payload.get("startTime"),
                    "end_time": payload.get("endTime"),
                    "entry_type": payload.get("entryType", "Arbeit"),
                    "cost_center": payload.get("costCenter"),
                    "work_area": payload.get("workArea"),
                    "notes": payload.get("notes"),
                },
            )
            self.db.commit()
        except Exception as exc:
            self.db.rollback()
            raise
        return self.get_zeiteintrag(entry_id)

    def approve_zeiteintrag(self, entry_id: str, approved_by: str) -> dict:
        self.get_zeiteintrag(entry_id)
        self.db.execute(
            text(
                "UPDATE domain_hr.time_bookings SET status = 'approved', approved_by = :approved_by, "
                "approved_at = now() WHERE id = :id AND tenant_id = :tenant_id"
            ),
            {"id": entry_id, "approved_by": approved_by, "tenant_id": self.tenant_id},
        )
        self.db.commit()
        return self.get_zeiteintrag(entry_id)

    # ── Abwesenheiten ─────────────────────────────────────────────────────────

    def list_abwesenheiten(
        self,
        mitarbeiter: Optional[str] = None,
        absence_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[dict]:
        params: dict[str, Any] = {"tenant_id": self.tenant_id}
        where = ["tenant_id = :tenant_id"]
        if mitarbeiter:
            params["mitarbeiter"] = mitarbeiter
            where.append("employee_ref = :mitarbeiter")
        if absence_type:
            params["absence_type"] = absence_type
            where.append("absence_type = :absence_type")
        if status:
            params["status"] = status
            where.append("status = :status")
        try:
            rows = self.db.execute(
                text(
                    f"SELECT id, employee_ref, work_date, absence_type, status, source, external_ref, notes "
                    f"FROM domain_hr.absences WHERE {' AND '.join(where)} "
                    f"ORDER BY work_date DESC LIMIT :limit OFFSET :skip"
                ),
                {**params, "limit": limit, "skip": skip},
            ).mappings().all()
            return [self._absence_to_dict(r) for r in rows]
        except Exception:
            logger.debug("absences table not available", exc_info=True)
            return []

    def import_abwesenheit(self, payload: dict) -> dict:
        absence_id = uuid7()
        try:
            # expand date range into daily records
            from_date = date.fromisoformat(payload["fromDate"])
            to_date = date.fromisoformat(payload["toDate"])
            inserted_ids: list[str] = []
            current = from_date
            while current <= to_date:
                row_id = uuid7()
                self.db.execute(
                    text(
                        "INSERT INTO domain_hr.absences "
                        "(id, tenant_id, employee_ref, work_date, absence_type, status, source, external_ref, notes) "
                        "VALUES (:id, :tid, :emp, :date, :type, :status, :src, :ext, :notes) "
                        "ON CONFLICT DO NOTHING"
                    ),
                    {
                        "id": row_id,
                        "tid": self.tenant_id,
                        "emp": payload["employeeRef"],
                        "date": current.isoformat(),
                        "type": payload.get("absenceType", "Urlaub"),
                        "status": payload.get("status", "Approved"),
                        "src": payload.get("sourceSystem", "urlaubsverwaltung"),
                        "ext": payload.get("externalRef"),
                        "notes": payload.get("note"),
                    },
                )
                inserted_ids.append(row_id)
                from datetime import timedelta
                current += timedelta(days=1)
            self.db.commit()
            return {"imported": len(inserted_ids), "ids": inserted_ids}
        except Exception as exc:
            self.db.rollback()
            raise

    # ── time profiles (domain_hr → domain_shared fallback) ───────────────────

    def list_time_profiles(
        self,
        status: Optional[str] = None,
        role: Optional[str] = None,
    ) -> tuple[list[dict], str]:
        params: dict[str, Any] = {"tenant_id": self.tenant_id}
        where = ["tenant_id = :tenant_id"]
        if status:
            params["status"] = status
            where.append("status = :status")
        if role:
            params["role"] = role
            where.append("role_code = :role")
        try:
            rows = self.db.execute(
                text(
                    f"SELECT employee_ref, display_name, role_code, role_label, location_code, "
                    f"department, manager_ref, employment_type, weekly_hours, time_model, "
                    f"cost_center, payroll_group, qualifications, can_drive, driver_card_id, "
                    f"vehicle_refs, calendar_provider, status "
                    f"FROM domain_hr.employee_time_profiles WHERE {' AND '.join(where)} "
                    f"ORDER BY location_code ASC, department ASC, display_name ASC"
                ),
                params,
            ).mappings().all()
            if rows:
                return [dict(r) for r in rows], "database"
        except Exception:
            pass

        # fallback: domain_shared.users
        try:
            user_rows = self.db.execute(
                text(
                    "SELECT id, username, email, first_name, last_name, roles, is_active, preferences "
                    "FROM domain_shared.users WHERE tenant_id = :tenant_id "
                    "ORDER BY last_name ASC, first_name ASC, username ASC"
                ),
                {"tenant_id": self.tenant_id},
            ).mappings().all()
            if user_rows:
                return [dict(r) for r in user_rows], "users-fallback"
        except Exception:
            pass

        return [], "empty"

    # ── private row mappers ───────────────────────────────────────────────────

    @staticmethod
    def _time_booking_to_dict(row: Any) -> dict:
        return {
            "id": str(row.get("id")),
            "employeeRef": str(row.get("employee_ref") or ""),
            "datum": to_iso(row.get("work_date")),
            "startTime": str(row.get("start_time")) if row.get("start_time") else None,
            "endTime": str(row.get("end_time")) if row.get("end_time") else None,
            "hours": float(row.get("total_hours") or 0),
            "entryType": str(row.get("entry_type") or "Arbeit"),
            "source": str(row.get("source") or "manual"),
            "status": str(row.get("status") or "pending"),
            "costCenter": row.get("cost_center"),
            "workArea": row.get("work_area"),
            "correctionReason": row.get("correction_reason"),
            "approvedBy": row.get("approved_by"),
            "approvedAt": to_iso(row.get("approved_at")) if row.get("approved_at") else None,
            "auditRef": row.get("audit_ref"),
        }

    @staticmethod
    def _absence_to_dict(row: Any) -> dict:
        status = str(row.get("status") or "Draft")
        planning_blockers: list[str] = []
        if status in {"Draft", "Submitted"}:
            planning_blockers.append("Abwesenheit ist noch nicht genehmigt")
        return {
            "id": str(row.get("id")),
            "employeeRef": str(row.get("employee_ref") or ""),
            "datum": to_iso(row.get("work_date")),
            "absenceType": str(row.get("absence_type") or "Urlaub"),
            "status": status,
            "source": str(row.get("source") or "manual"),
            "externalRef": row.get("external_ref"),
            "planningBlockers": planning_blockers,
            "note": row.get("notes"),
        }
