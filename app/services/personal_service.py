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

    # ── Zeiteinträge (domain_hr.time_entries) ────────────────────────────────

    _TIME_ENTRY_COLS = (
        "id, employee_ref, entry_date, start_time, end_time, hours, entry_type, "
        "source, status, cost_center, work_area, correction_reason, approved_by, approved_at, audit_ref"
    )
    _ABSENCE_ENTRY_TYPES = ("'Urlaub'", "'Krank'", "'Unbezahlt'", "'Sonstiges'")

    def list_zeiteintraege(
        self,
        datum: Optional[str] = None,
        mitarbeiter: Optional[str] = None,
        datum_von: Optional[str] = None,
        datum_bis: Optional[str] = None,
    ) -> list[dict]:
        params: dict[str, Any] = {"tenant_id": self.tenant_id}
        where = ["tenant_id = :tenant_id"]
        if datum:
            params["entry_date"] = datum
            where.append("entry_date = :entry_date")
        if mitarbeiter:
            params["employee_ref"] = mitarbeiter
            where.append("employee_ref = :employee_ref")
        if datum_von:
            params["datum_von"] = datum_von
            where.append("entry_date >= :datum_von")
        if datum_bis:
            params["datum_bis"] = datum_bis
            where.append("entry_date <= :datum_bis")

        try:
            rows = self.db.execute(
                text(
                    f"SELECT {self._TIME_ENTRY_COLS} FROM domain_hr.time_entries "
                    f"WHERE {' AND '.join(where)} ORDER BY entry_date DESC, employee_ref ASC"
                ),
                params,
            ).mappings().all()
            return [self._time_entry_to_dict(r) for r in rows]
        except Exception:
            logger.debug("time_entries table not available", exc_info=True)
            return []

    def get_zeiteintrag(self, entry_id: str) -> dict:
        row = self.db.execute(
            text(
                f"SELECT {self._TIME_ENTRY_COLS} FROM domain_hr.time_entries "
                f"WHERE id = :id AND tenant_id = :tenant_id"
            ),
            {"id": entry_id, "tenant_id": self.tenant_id},
        ).mappings().first()
        if not row:
            raise EntityNotFoundError("Zeiteintrag", entry_id)
        return self._time_entry_to_dict(row)

    def create_zeiteintrag(self, payload: dict) -> dict:
        from uuid import uuid4
        entry_id = str(uuid4())
        row = self.db.execute(
            text(
                "INSERT INTO domain_hr.time_entries "
                "(id, tenant_id, employee_ref, entry_date, start_time, end_time, hours, "
                "entry_type, source, status, cost_center, work_area, notes, created_at, updated_at) "
                "VALUES (:id, :tenant_id, :employee_ref, :entry_date, :start_time, :end_time, :hours, "
                ":entry_type, :source, 'Draft', :cost_center, :work_area, :notes, NOW(), NOW()) "
                f"RETURNING {self._TIME_ENTRY_COLS}"
            ),
            {
                "id": entry_id,
                "tenant_id": self.tenant_id,
                "employee_ref": payload["employeeRef"],
                "entry_date": payload["datum"],
                "start_time": payload.get("startTime"),
                "end_time": payload.get("endTime"),
                "hours": payload["hours"],
                "entry_type": payload.get("entryType", "Arbeit"),
                "source": payload.get("source", "manual"),
                "cost_center": payload.get("costCenter"),
                "work_area": payload.get("workArea"),
                "notes": payload.get("notes"),
            },
        ).mappings().first()
        self.db.commit()
        return self._time_entry_to_dict(row)

    def submit_zeiteintrag(self, entry_id: str) -> dict:
        row = self.db.execute(
            text(
                "UPDATE domain_hr.time_entries "
                "SET status = 'Submitted', updated_at = NOW(), version = version + 1 "
                "WHERE id = :id AND tenant_id = :tenant_id "
                "  AND status IN ('Draft', 'Rejected', 'Corrected') "
                f"RETURNING {self._TIME_ENTRY_COLS}"
            ),
            {"id": entry_id, "tenant_id": self.tenant_id},
        ).mappings().first()
        if not row:
            from app.core.exceptions import ConflictError
            raise ConflictError("Zeitbuchung kann in diesem Status nicht eingereicht werden")
        self.db.commit()
        return self._time_entry_to_dict(row)

    def approve_zeiteintrag(self, entry_id: str, approved_by: str) -> dict:
        row = self.db.execute(
            text(
                "UPDATE domain_hr.time_entries "
                "SET status = 'Approved', approved_by = :approved_by, "
                "    approved_at = NOW(), updated_at = NOW(), version = version + 1 "
                "WHERE id = :id AND tenant_id = :tenant_id AND status = 'Submitted' "
                f"RETURNING {self._TIME_ENTRY_COLS}"
            ),
            {"id": entry_id, "tenant_id": self.tenant_id, "approved_by": approved_by},
        ).mappings().first()
        if not row:
            from app.core.exceptions import ConflictError
            raise ConflictError("Zeitbuchung muss vor Freigabe eingereicht sein")
        self.db.commit()
        return self._time_entry_to_dict(row)

    def correct_zeiteintrag(self, entry_id: str, payload: dict) -> dict:
        current = self.db.execute(
            text("SELECT status FROM domain_hr.time_entries WHERE id = :id AND tenant_id = :tenant_id"),
            {"id": entry_id, "tenant_id": self.tenant_id},
        ).mappings().first()
        if not current:
            raise EntityNotFoundError("Zeiteintrag", entry_id)
        if str(current.get("status")) == "Exported":
            from app.core.exceptions import ValidationFailedError
            raise ValidationFailedError("Exportierte Zeitbuchungen duerfen nicht still veraendert werden")

        row = self.db.execute(
            text(
                "UPDATE domain_hr.time_entries SET "
                "start_time = :start_time, end_time = :end_time, hours = :hours, "
                "entry_type = :entry_type, status = 'Corrected', cost_center = :cost_center, "
                "work_area = :work_area, correction_reason = :correction_reason, "
                "notes = :notes, updated_at = NOW(), version = version + 1 "
                "WHERE id = :id AND tenant_id = :tenant_id "
                f"RETURNING {self._TIME_ENTRY_COLS}"
            ),
            {
                "id": entry_id,
                "tenant_id": self.tenant_id,
                "start_time": payload.get("startTime"),
                "end_time": payload.get("endTime"),
                "hours": payload["hours"],
                "entry_type": payload.get("entryType", "Arbeit"),
                "cost_center": payload.get("costCenter"),
                "work_area": payload.get("workArea"),
                "correction_reason": payload["correctionReason"],
                "notes": payload.get("notes"),
            },
        ).mappings().first()
        self.db.commit()
        return self._time_entry_to_dict(row)

    # ── Abwesenheiten (domain_hr.time_entries, entry_type IN absences) ────────

    def list_abwesenheiten(
        self,
        datum_von: Optional[str] = None,
        datum_bis: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[dict]:
        absence_filter = f"entry_type IN ({', '.join(self._ABSENCE_ENTRY_TYPES)})"
        params: dict[str, Any] = {"tenant_id": self.tenant_id}
        where = ["tenant_id = :tenant_id", absence_filter]
        if datum_von:
            params["datum_von"] = datum_von
            where.append("entry_date >= :datum_von")
        if datum_bis:
            params["datum_bis"] = datum_bis
            where.append("entry_date <= :datum_bis")
        if status:
            params["status"] = status
            where.append("status = :status")

        try:
            rows = self.db.execute(
                text(
                    f"SELECT id, employee_ref, entry_date, entry_type, source, status, notes, audit_ref "
                    f"FROM domain_hr.time_entries WHERE {' AND '.join(where)} "
                    f"ORDER BY entry_date ASC, employee_ref ASC"
                ),
                params,
            ).mappings().all()
            return [self._absence_to_dict(r) for r in rows]
        except Exception:
            logger.debug("time_entries table not available for absences", exc_info=True)
            return []

    def import_abwesenheit(self, payload: dict) -> tuple[list[dict], int]:
        from datetime import timedelta
        from uuid import uuid4
        from_date = date.fromisoformat(payload["fromDate"])
        to_date = date.fromisoformat(payload["toDate"])
        if to_date < from_date:
            from app.core.exceptions import ValidationFailedError
            raise ValidationFailedError("toDate must be on or after fromDate")

        rows_out: list[dict] = []
        current = from_date
        while current <= to_date:
            row = self.db.execute(
                text(
                    "INSERT INTO domain_hr.time_entries "
                    "(id, tenant_id, employee_ref, entry_date, start_time, end_time, hours, "
                    "entry_type, source, status, notes, audit_ref, created_at, updated_at) "
                    "VALUES (:id, :tenant_id, :employee_ref, :entry_date, NULL, NULL, 0, "
                    ":entry_type, 'absence', :status, :notes, :audit_ref, NOW(), NOW()) "
                    "RETURNING id, employee_ref, entry_date, entry_type, source, status, notes, audit_ref"
                ),
                {
                    "id": str(uuid4()),
                    "tenant_id": self.tenant_id,
                    "employee_ref": payload["employeeRef"],
                    "entry_date": current.isoformat(),
                    "entry_type": payload.get("absenceType", "Urlaub"),
                    "status": payload.get("status", "Approved"),
                    "notes": payload.get("note") or payload.get("sourceSystem"),
                    "audit_ref": payload.get("externalRef") or f"{payload.get('sourceSystem', 'import')}:{payload['employeeRef']}:{current.isoformat()}",
                },
            ).mappings().first()
            rows_out.append(self._absence_to_dict(row))
            current += timedelta(days=1)
        self.db.commit()
        return rows_out, len(rows_out)

    def delete_abwesenheit(self, absence_id: str) -> None:
        row = self.db.execute(
            text(
                f"SELECT id, status FROM domain_hr.time_entries "
                f"WHERE id = :id AND tenant_id = :tenant_id "
                f"AND entry_type IN ({', '.join(self._ABSENCE_ENTRY_TYPES)})"
            ),
            {"id": absence_id, "tenant_id": self.tenant_id},
        ).fetchone()
        if not row:
            raise EntityNotFoundError("Abwesenheit", absence_id)
        if str(row[1]) in ("Approved", "Genehmigt"):
            from app.core.exceptions import ValidationFailedError
            raise ValidationFailedError("Genehmigte Abwesenheiten können nicht gelöscht werden")
        self.db.execute(
            text("DELETE FROM domain_hr.time_entries WHERE id = :id AND tenant_id = :tenant_id"),
            {"id": absence_id, "tenant_id": self.tenant_id},
        )
        self.db.commit()

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
    def _time_entry_to_dict(row: Any) -> dict:
        r = dict(row) if row else {}
        st = r.get("start_time")
        et = r.get("end_time")
        ap = r.get("approved_at")
        return {
            "id": str(r.get("id") or ""),
            "employeeRef": str(r.get("employee_ref") or ""),
            "datum": to_iso(r.get("entry_date")),
            "startTime": str(st) if st else None,
            "endTime": str(et) if et else None,
            "hours": float(r.get("hours") or 0),
            "entryType": str(r.get("entry_type") or "Arbeit"),
            "source": str(r.get("source") or "manual"),
            "status": str(r.get("status") or "Draft"),
            "costCenter": str(r.get("cost_center") or "") or None,
            "workArea": str(r.get("work_area") or "") or None,
            "correctionReason": str(r.get("correction_reason") or "") or None,
            "approvedBy": str(r.get("approved_by") or "") or None,
            "approvedAt": to_iso(ap) if ap else None,
            "auditRef": str(r.get("audit_ref") or "") or None,
        }

    @staticmethod
    def _absence_to_dict(row: Any) -> dict:
        r = dict(row) if row else {}
        status = str(r.get("status") or "Draft")
        if status in {"Approved", "Genehmigt"}:
            blockers = ["tour", "shift", "calendar", "payroll"]
        elif status == "Submitted":
            blockers = ["planning-review"]
        else:
            blockers = []
        return {
            "id": str(r.get("id") or ""),
            "employeeRef": str(r.get("employee_ref") or ""),
            "datum": to_iso(r.get("entry_date")),
            "absenceType": str(r.get("entry_type") or "Urlaub"),
            "status": status,
            "source": str(r.get("source") or "absence"),
            "externalRef": str(r.get("audit_ref") or "") or None,
            "planningBlockers": blockers,
            "note": str(r.get("notes") or "") or None,
        }
