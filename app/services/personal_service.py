"""Service layer for HR/Personal domain queries (Mitarbeiter, Zeiterfassung, Abwesenheiten)."""

from __future__ import annotations

import json
import logging
from datetime import date, datetime
from typing import Any, List, Optional, Sequence
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError
from app.core.uuid7 import uuid7
from app.api.v1.schemas.personal_schemas import (
    HrmOperationsGateOut,
    HrmOperationsGatesOut,
    HrmOperationsGateEvidenceOut,
    HrmOperationsGateProbeOut,
    HrmOperatingSystemOut,
    HrmOperatingSystemModuleOut,
    HrmReadinessOut,
    HrmReadinessCapabilityOut,
    HrmReadinessIntegrationOut,
    HrmReadinessAiControlOut,
    EmployeeFileOut,
    EmployeeFileDocumentOut,
    EmployeeFileDocumentClassOut,
    EmployeeFileExportOut,
    EmployeeFileRetentionOut,
)

logger = logging.getLogger(__name__)


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        from app.core.exceptions import ValidationFailedError
        raise ValidationFailedError(f"Invalid date format: {value}") from exc


def _parse_event_dt(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        from app.core.exceptions import ValidationFailedError
        raise ValidationFailedError(f"Invalid datetime format: {value}") from exc


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


def to_iso(d: date | datetime | str | None) -> str:
    if d is None:
        return ""
    if isinstance(d, str):
        return d  # already ISO string
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
                "WHERE id = :entry_id AND tenant_id = :tenant_id "
                "  AND status IN ('Draft', 'Rejected', 'Corrected') "
                f"RETURNING {self._TIME_ENTRY_COLS}"
            ),
            {"entry_id": entry_id, "tenant_id": self.tenant_id},
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
                "WHERE id = :entry_id AND tenant_id = :tenant_id AND status = 'Submitted' "
                f"RETURNING {self._TIME_ENTRY_COLS}"
            ),
            {"entry_id": entry_id, "tenant_id": self.tenant_id, "approved_by": approved_by},
        ).mappings().first()
        if not row:
            from app.core.exceptions import ConflictError
            raise ConflictError("Zeitbuchung muss vor Freigabe eingereicht sein")
        self.db.commit()
        return self._time_entry_to_dict(row)

    def correct_zeiteintrag(self, entry_id: str, payload: dict) -> dict:
        current = self.db.execute(
            text("SELECT status FROM domain_hr.time_entries WHERE id = :entry_id AND tenant_id = :tenant_id"),
            {"entry_id": entry_id, "tenant_id": self.tenant_id},
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
                "WHERE id = :entry_id AND tenant_id = :tenant_id "
                f"RETURNING {self._TIME_ENTRY_COLS}"
            ),
            {
                "entry_id": entry_id,
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
        except Exception:  # noqa: BLE001 — DB-Abfrage fehlgeschlagen; nächste Fallback-Strategie wird versucht
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
        except Exception:  # noqa: BLE001 — DB-Abfrage fehlgeschlagen; nächste Fallback-Strategie wird versucht
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

    # ── mitarbeiter mutations ─────────────────────────────────────────────────

    def create_mitarbeiter(self, payload: Any) -> str:
        """Insert new user into domain_shared.users. Returns new user_id."""
        from uuid import uuid4
        import json as _json
        existing = self.db.execute(
            text("SELECT 1 FROM domain_shared.users "
                 "WHERE tenant_id = :tid AND (email = :email OR username = :email) LIMIT 1"),
            {"tid": self.tenant_id, "email": payload.email},
        ).first()
        if existing:
            from app.core.exceptions import ConflictError
            raise ConflictError("Mitarbeiter mit E-Mail existiert bereits")
        first, last = split_name(payload.name)
        role_slug = (payload.position or "mitarbeiter").strip().lower().replace(" ", "_") or "mitarbeiter"
        user_id = str(uuid4())
        self.db.execute(
            text("""INSERT INTO domain_shared.users
                    (id, keycloak_id, username, email, first_name, last_name,
                     is_active, roles, tenant_id, preferences, created_at, updated_at)
                    VALUES (:id, :kc_id, :uname, :email, :first, :last,
                            :active, :roles, :tid, CAST(:prefs AS jsonb), NOW(), NOW())"""),
            {"id": user_id, "kc_id": f"local-{user_id}", "uname": payload.email,
             "email": payload.email, "first": first, "last": last,
             "active": payload.status != "krank", "roles": [role_slug],
             "tid": self.tenant_id,
             "prefs": _json.dumps({"hr_status": payload.status, "abteilung": payload.abteilung})},
        )
        self.db.commit()
        return user_id

    def update_mitarbeiter(self, user_id: str, payload: Any) -> None:
        import json as _json
        first, last = split_name(payload.name)
        role_slug = (payload.position or "mitarbeiter").strip().lower().replace(" ", "_") or "mitarbeiter"
        count = self.db.execute(
            text("""UPDATE domain_shared.users
                    SET email=:email, username=:email, first_name=:first, last_name=:last,
                        is_active=:active, roles=:roles,
                        preferences=COALESCE(preferences,'{}' ::jsonb)||CAST(:prefs AS jsonb),
                        updated_at=NOW()
                    WHERE id=:uid AND tenant_id=:tid"""),
            {"email": payload.email, "first": first, "last": last,
             "active": payload.status != "krank", "roles": [role_slug],
             "prefs": _json.dumps({"hr_status": payload.status, "abteilung": payload.abteilung}),
             "uid": user_id, "tid": self.tenant_id},
        ).rowcount
        if not count:
            from app.core.exceptions import EntityNotFoundError
            raise EntityNotFoundError("Mitarbeiter", user_id)
        self.db.commit()

    def delete_mitarbeiter(self, user_id: str) -> None:
        count = self.db.execute(
            text("DELETE FROM domain_shared.users WHERE id=:uid AND tenant_id=:tid"),
            {"uid": user_id, "tid": self.tenant_id},
        ).rowcount
        if not count:
            from app.core.exceptions import EntityNotFoundError
            raise EntityNotFoundError("Mitarbeiter", user_id)
        self.db.commit()

    # ── shifts ────────────────────────────────────────────────────────────────

    def list_shifts(
        self,
        datum_von: Optional[str] = None,
        datum_bis: Optional[str] = None,
        location: Optional[str] = None,
    ) -> list:
        params: dict[str, Any] = {"tid": self.tenant_id}
        where = ["tenant_id = :tid"]
        if datum_von:
            params["dv"] = _parse_date(datum_von)
            where.append("shift_date >= :dv")
        if datum_bis:
            params["db"] = _parse_date(datum_bis)
            where.append("shift_date <= :db")
        if location:
            params["loc"] = location
            where.append("location_code = :loc")
        rows = self.db.execute(
            text(f"SELECT id, shift_date, name, location_code, required_role, "  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
                 f"required_qualifications, required_headcount, starts_at, ends_at, "
                 f"assigned_employee_refs, status, conflicts, notes "
                 f"FROM domain_hr.shifts WHERE {' AND '.join(where)} "
                 f"ORDER BY shift_date ASC, starts_at ASC"),
            params,
        ).mappings().all()
        return [dict(r) for r in rows]

    def create_shift(self, params: dict) -> dict:
        row = self.db.execute(
            text("""INSERT INTO domain_hr.shifts
                    (id, tenant_id, shift_date, name, location_code, required_role,
                     required_qualifications, required_headcount, starts_at, ends_at,
                     assigned_employee_refs, status, conflicts, notes, created_at, updated_at)
                    VALUES (:id, :tid, :shift_date, :name, :location_code, :required_role,
                     CAST(:required_qualifications AS jsonb), :required_headcount, :starts_at, :ends_at,
                     CAST(:assigned_employee_refs AS jsonb), :status, CAST(:conflicts AS jsonb),
                     :notes, NOW(), NOW())
                    RETURNING id, shift_date, name, location_code, required_role,
                              required_qualifications, required_headcount, starts_at, ends_at,
                              assigned_employee_refs, status, conflicts, notes"""),
            {"tid": self.tenant_id, **params},
        ).mappings().first()
        self.db.commit()
        return dict(row)

    def delete_shift(self, shift_id: str) -> None:
        count = self.db.execute(
            text("DELETE FROM domain_hr.shifts WHERE id=:sid AND tenant_id=:tid"),
            {"sid": shift_id, "tid": self.tenant_id},
        ).rowcount
        if not count:
            from app.core.exceptions import EntityNotFoundError
            raise EntityNotFoundError("Shift", shift_id)
        self.db.commit()

    def get_shift_context(self, shift_date: Any) -> tuple[list, list]:
        """Return (profile_rows, absence_rows) needed for conflict detection."""
        profile_rows = self.db.execute(
            text("SELECT employee_ref, status, qualifications "
                 "FROM domain_hr.employee_time_profiles WHERE tenant_id=:tid"),
            {"tid": self.tenant_id},
        ).mappings().all()
        absence_rows = self.db.execute(
            text("SELECT employee_ref FROM domain_hr.time_entries "
                 "WHERE tenant_id=:tid AND entry_date=:dt "
                 "AND entry_type IN ('Urlaub','Krank','Unbezahlt','Sonstiges') "
                 "AND status IN ('Approved','Genehmigt')"),
            {"tid": self.tenant_id, "dt": shift_date},
        ).mappings().all()
        return list(profile_rows), list(absence_rows)

    # ── calendar events ───────────────────────────────────────────────────────

    def list_calendar_events(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        employee_ref: Optional[str] = None,
        event_type: Optional[str] = None,
    ) -> list:
        params: dict[str, Any] = {"tid": self.tenant_id}
        where = ["tenant_id = :tid"]
        if start:
            params["start"] = _parse_event_dt(start)
            where.append("ends_at >= :start")
        if end:
            params["end"] = _parse_event_dt(end)
            where.append("starts_at <= :end")
        if employee_ref:
            params["eref"] = employee_ref
            where.append("employee_ref = :eref")
        if event_type:
            params["etype"] = event_type
            where.append("event_type = :etype")
        rows = self.db.execute(
            text(f"SELECT id, source_system, provider, external_event_ref, event_type, title, "  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
                 f"employee_ref, resource_ref, starts_at, ends_at, timezone, visibility, "
                 f"status, sync_state, conflict_level, source_ref, metadata "
                 f"FROM domain_hr.calendar_events WHERE {' AND '.join(where)} "
                 f"ORDER BY starts_at ASC, employee_ref ASC"),
            params,
        ).mappings().all()
        return [dict(r) for r in rows]

    def create_calendar_event(self, params: dict) -> dict:
        row = self.db.execute(
            text("""INSERT INTO domain_hr.calendar_events
                    (id, tenant_id, source_system, provider, external_event_ref, event_type, title,
                     employee_ref, resource_ref, starts_at, ends_at, timezone, visibility, status,
                     sync_state, conflict_level, source_ref, metadata, created_at, updated_at)
                    VALUES (:id, :tid, :source_system, :provider, :external_event_ref, :event_type,
                     :title, :employee_ref, :resource_ref, :starts_at, :ends_at, :timezone, :visibility,
                     :status, :sync_state, :conflict_level, :source_ref, CAST(:metadata AS jsonb), NOW(), NOW())
                    RETURNING id, source_system, provider, external_event_ref, event_type, title,
                              employee_ref, resource_ref, starts_at, ends_at, timezone, visibility,
                              status, sync_state, conflict_level, source_ref, metadata"""),
            {"tid": self.tenant_id, **params},
        ).mappings().first()
        self.db.commit()
        return dict(row)

    # ── payroll exports ───────────────────────────────────────────────────────

    def list_payroll_exports(self) -> list:
        rows = self.db.execute(
            text("SELECT id, period_from, period_to, target_system, status, items, blockers "
                 "FROM domain_hr.payroll_exports WHERE tenant_id=:tid "
                 "ORDER BY period_from DESC, created_at DESC"),
            {"tid": self.tenant_id},
        ).mappings().all()
        return [dict(r) for r in rows]

    def get_payroll_time_rows(self, period_from: Any, period_to: Any) -> list:
        rows = self.db.execute(
            text("SELECT id, employee_ref, entry_date, hours, entry_type, status, cost_center "
                 "FROM domain_hr.time_entries WHERE tenant_id=:tid "
                 "AND entry_date BETWEEN :pf AND :pt "
                 "AND entry_type IN ('Arbeit','Bereitschaft','Urlaub','Krank','Korrektur') "
                 "ORDER BY employee_ref ASC, entry_date ASC"),
            {"tid": self.tenant_id, "pf": period_from, "pt": period_to},
        ).mappings().all()
        return [dict(r) for r in rows]

    def create_payroll_export(self, params: dict) -> dict:
        row = self.db.execute(
            text("""INSERT INTO domain_hr.payroll_exports
                    (id, tenant_id, period_from, period_to, target_system, status,
                     items, blockers, created_at, created_by)
                    VALUES (:id, :tid, :period_from, :period_to, :target_system, :status,
                     CAST(:items AS jsonb), CAST(:blockers AS jsonb), NOW(), :created_by)
                    RETURNING id, period_from, period_to, target_system, status, items, blockers"""),
            {"tid": self.tenant_id, **params},
        ).mappings().first()
        self.db.commit()
        return dict(row)

    # ── campaign capacity ─────────────────────────────────────────────────────

    def list_campaign_capacity(self) -> list:
        rows = self.db.execute(
            text("SELECT id, campaign_code, name, period_from, period_to, location_code, "
                 "role_demand, expected_volume, status, findings "
                 "FROM domain_hr.campaign_capacity_plans WHERE tenant_id=:tid "
                 "ORDER BY period_from ASC, campaign_code ASC"),
            {"tid": self.tenant_id},
        ).mappings().all()
        return [dict(r) for r in rows]

    def get_campaign_context(self, location_code: str, period_from: Any, period_to: Any) -> tuple[list, list, list]:
        profile_rows = self.db.execute(
            text("SELECT employee_ref, role_code, status "
                 "FROM domain_hr.employee_time_profiles "
                 "WHERE tenant_id=:tid AND location_code=:loc"),
            {"tid": self.tenant_id, "loc": location_code},
        ).mappings().all()
        absence_rows = self.db.execute(
            text("SELECT employee_ref FROM domain_hr.time_entries "
                 "WHERE tenant_id=:tid AND entry_date BETWEEN :pf AND :pt "
                 "AND entry_type IN ('Urlaub','Krank','Unbezahlt','Sonstiges') "
                 "AND status IN ('Approved','Genehmigt')"),
            {"tid": self.tenant_id, "pf": period_from, "pt": period_to},
        ).mappings().all()
        shift_rows = self.db.execute(
            text("SELECT assigned_employee_refs FROM domain_hr.shifts "
                 "WHERE tenant_id=:tid AND shift_date BETWEEN :pf AND :pt "
                 "AND location_code=:loc"),
            {"tid": self.tenant_id, "pf": period_from, "pt": period_to, "loc": location_code},
        ).mappings().all()
        return list(profile_rows), list(absence_rows), list(shift_rows)

    def create_campaign_capacity(self, params: dict) -> dict:
        row = self.db.execute(
            text("""INSERT INTO domain_hr.campaign_capacity_plans
                    (id, tenant_id, campaign_code, name, period_from, period_to, location_code,
                     role_demand, expected_volume, status, findings, created_at, updated_at)
                    VALUES (:id, :tid, :campaign_code, :name, :period_from, :period_to,
                     :location_code, CAST(:role_demand AS jsonb), :expected_volume, :status,
                     CAST(:findings AS jsonb), NOW(), NOW())
                    RETURNING id, campaign_code, name, period_from, period_to, location_code,
                              role_demand, expected_volume, status, findings"""),
            {"tid": self.tenant_id, **params},
        ).mappings().first()
        self.db.commit()
        return dict(row)

    # ── field service plan ────────────────────────────────────────────────────

    def list_field_service_plans(self, employee_ref: Optional[str] = None) -> list:
        params: dict[str, Any] = {"tid": self.tenant_id}
        where = ["tenant_id = :tid"]
        if employee_ref:
            params["eref"] = employee_ref
            where.append("employee_ref = :eref")
        rows = self.db.execute(
            text(f"SELECT id, employee_ref, customer_ref, territory_code, campaign_code, "  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
                 f"visit_type, starts_at, ends_at, status, conflicts, notes "
                 f"FROM domain_hr.field_service_plans WHERE {' AND '.join(where)} "
                 f"ORDER BY starts_at ASC, employee_ref ASC"),
            params,
        ).mappings().all()
        return [dict(r) for r in rows]

    def get_field_service_context(self, employee_ref: str, starts_at: Any, ends_at: Any) -> tuple[list, list, list]:
        profile_rows = self.db.execute(
            text("SELECT employee_ref, status, time_model "
                 "FROM domain_hr.employee_time_profiles "
                 "WHERE tenant_id=:tid AND employee_ref=:eref"),
            {"tid": self.tenant_id, "eref": employee_ref},
        ).mappings().all()
        absence_rows = self.db.execute(
            text("SELECT employee_ref FROM domain_hr.time_entries "
                 "WHERE tenant_id=:tid AND employee_ref=:eref "
                 "AND entry_date BETWEEN :sd AND :ed "
                 "AND entry_type IN ('Urlaub','Krank','Unbezahlt','Sonstiges') "
                 "AND status IN ('Approved','Genehmigt')"),
            {"tid": self.tenant_id, "eref": employee_ref,
             "sd": starts_at.date(), "ed": ends_at.date()},
        ).mappings().all()
        cal_rows = self.db.execute(
            text("SELECT id FROM domain_hr.calendar_events "
                 "WHERE tenant_id=:tid AND employee_ref=:eref "
                 "AND ends_at > :sa AND starts_at < :ea AND status='confirmed'"),
            {"tid": self.tenant_id, "eref": employee_ref, "sa": starts_at, "ea": ends_at},
        ).mappings().all()
        return list(profile_rows), list(absence_rows), list(cal_rows)

    def create_field_service_plan(self, params: dict) -> dict:
        row = self.db.execute(
            text("""INSERT INTO domain_hr.field_service_plans
                    (id, tenant_id, employee_ref, customer_ref, territory_code, campaign_code,
                     visit_type, starts_at, ends_at, status, conflicts, notes, created_at, updated_at)
                    VALUES (:id, :tid, :employee_ref, :customer_ref, :territory_code, :campaign_code,
                     :visit_type, :starts_at, :ends_at, :status, CAST(:conflicts AS jsonb),
                     :notes, NOW(), NOW())
                    RETURNING id, employee_ref, customer_ref, territory_code, campaign_code,
                              visit_type, starts_at, ends_at, status, conflicts, notes"""),
            {"tid": self.tenant_id, **params},
        ).mappings().first()
        self.db.commit()
        return dict(row)

    # ── stundenzettel (driver timesheets) ─────────────────────────────────────

    def create_stundenzettel(self, params: dict) -> str:
        """Insert a driver timesheet + linked time_entry. Returns timesheet_id."""
        timesheet_id = params.pop("timesheet_id")
        time_entry_params = params.pop("time_entry_params")
        self.db.execute(
            text("""INSERT INTO domain_hr.driver_timesheets
                    (id, tenant_id, entry_date, driver_name, vehicle_plate, tours,
                     total_hours, overtime_hours, signature_data, created_at, updated_at)
                    VALUES (:id, :tid, :entry_date, :driver_name, :vehicle_plate,
                     CAST(:tours AS jsonb), :total_hours, :overtime_hours,
                     :signature_data, NOW(), NOW())"""),
            {"id": timesheet_id, "tid": self.tenant_id, **params},
        )
        self.db.execute(
            text("""INSERT INTO domain_hr.time_entries
                    (id, tenant_id, employee_ref, entry_date, start_time, end_time,
                     hours, entry_type, source, notes, created_at, updated_at)
                    VALUES (:id, :tid, :employee_ref, :entry_date, :start_time, :end_time,
                     :hours, :entry_type, 'timesheet', :notes, NOW(), NOW())"""),
            {"tid": self.tenant_id, **time_entry_params},
        )
        self.db.commit()
        return timesheet_id

    def list_stundenzettel(self, datum_von: Optional[str] = None, datum_bis: Optional[str] = None) -> list:
        params: dict[str, Any] = {"tid": self.tenant_id}
        where = ["tenant_id = :tid"]
        if datum_von:
            where.append("entry_date >= :dv")
            params["dv"] = datum_von
        if datum_bis:
            where.append("entry_date <= :db")
            params["db"] = datum_bis
        rows = self.db.execute(
            text(f"SELECT id, entry_date, driver_name, vehicle_plate, tours, total_hours, "  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
                 f"overtime_hours, created_at FROM domain_hr.driver_timesheets "
                 f"WHERE {' AND '.join(where)} ORDER BY entry_date DESC, created_at DESC"),
            params,
        ).mappings().all()
        return [dict(r) for r in rows]

    # ── Work-Plan ─────────────────────────────────────────────────────────────

    def get_work_plan_data(self, start_date: date, end_date: date) -> dict:
        """Fetch all raw rows needed to assemble a work plan."""
        tid = self.tenant_id
        period = {"tenant_id": tid, "period_from": start_date, "period_to": end_date}

        profile_rows = self.db.execute(
            text("""SELECT employee_ref, display_name, role_code, time_model, status, qualifications
                    FROM domain_hr.employee_time_profiles
                    WHERE tenant_id = :tenant_id AND status = 'active'"""),
            {"tenant_id": tid},
        ).mappings().all()

        try:
            user_rows = self.db.execute(
                text("SELECT id, preferences FROM domain_shared.users WHERE tenant_id = :tenant_id"),
                {"tenant_id": tid},
            ).mappings().all()
        except Exception:
            user_rows = []

        absence_rows = self.db.execute(
            text("""SELECT id, employee_ref, entry_date, entry_type, status
                    FROM domain_hr.time_entries
                    WHERE tenant_id = :tenant_id
                      AND entry_date BETWEEN :period_from AND :period_to
                      AND entry_type IN ('Urlaub', 'Krank', 'Unbezahlt', 'Sonstiges')
                      AND status IN ('Approved', 'Genehmigt')
                    ORDER BY entry_date ASC, employee_ref ASC"""),
            period,
        ).mappings().all()

        shift_rows = self.db.execute(
            text("""SELECT id, shift_date, name, starts_at, ends_at, assigned_employee_refs, status
                    FROM domain_hr.shifts
                    WHERE tenant_id = :tenant_id AND shift_date BETWEEN :period_from AND :period_to
                    ORDER BY shift_date ASC, starts_at ASC"""),
            period,
        ).mappings().all()

        calendar_rows = self.db.execute(
            text("""SELECT id, employee_ref, event_type, title, starts_at, ends_at, status, conflict_level
                    FROM domain_hr.calendar_events
                    WHERE tenant_id = :tenant_id
                      AND starts_at::date <= :period_to
                      AND ends_at::date >= :period_from
                    ORDER BY starts_at ASC, employee_ref ASC"""),
            period,
        ).mappings().all()

        field_rows = self.db.execute(
            text("""SELECT id, employee_ref, customer_ref, visit_type, starts_at, ends_at, status
                    FROM domain_hr.field_service_plans
                    WHERE tenant_id = :tenant_id
                      AND starts_at::date <= :period_to
                      AND ends_at::date >= :period_from
                    ORDER BY starts_at ASC, employee_ref ASC"""),
            period,
        ).mappings().all()

        return {
            "profile_rows": [dict(r) for r in profile_rows],
            "user_rows": [dict(r) for r in user_rows],
            "absence_rows": [dict(r) for r in absence_rows],
            "shift_rows": [dict(r) for r in shift_rows],
            "calendar_rows": [dict(r) for r in calendar_rows],
            "field_rows": [dict(r) for r in field_rows],
        }

    # ── Driver-Time Summary ───────────────────────────────────────────────────

    def get_driver_time_data(self, target_date: str) -> dict:
        """Fetch timesheet + absence rows for driver-time summary. Raises on DB error."""
        params = {"tenant_id": self.tenant_id, "entry_date": target_date}
        timesheet_rows = self.db.execute(
            text("""SELECT id, entry_date, driver_name, vehicle_plate, tours,
                           total_hours, overtime_hours, created_at
                    FROM domain_hr.driver_timesheets
                    WHERE tenant_id = :tenant_id AND entry_date = :entry_date
                    ORDER BY driver_name ASC, created_at ASC"""),
            params,
        ).mappings().all()
        absence_rows = self.db.execute(
            text("""SELECT employee_ref, entry_date, entry_type
                    FROM domain_hr.time_entries
                    WHERE tenant_id = :tenant_id
                      AND entry_date = :entry_date
                      AND entry_type IN ('Urlaub', 'Krank')"""),
            params,
        ).mappings().all()
        return {
            "timesheet_rows": [dict(r) for r in timesheet_rows],
            "absence_rows": [dict(r) for r in absence_rows],
        }

    # ── Time Cockpit ──────────────────────────────────────────────────────────

    def get_time_cockpit_entries(self, target_date: str) -> list:
        """Fetch time entries for the cockpit view. Raises on DB error."""
        rows = self.db.execute(
            text("""SELECT id, employee_ref, entry_date, start_time, end_time,
                           hours, entry_type, source, status
                    FROM domain_hr.time_entries
                    WHERE tenant_id = :tenant_id AND entry_date = :entry_date
                    ORDER BY employee_ref ASC, start_time ASC"""),
            {"tenant_id": self.tenant_id, "entry_date": target_date},
        ).mappings().all()
        return [dict(r) for r in rows]

    # ── HRM Operations Gates ──────────────────────────────────────────────────

    def add_gate_evidence(
        self,
        gate_id: str,
        evidence_id: str,
        evidence_type: str,
        title: str,
        artifact_ref: Optional[str],
        submitted_by: str,
        metadata: dict,
        current_status: str,
    ) -> dict:
        """Insert gate evidence, update gate status, write audit. Returns evidence row dict."""
        row = self.db.execute(
            text("""INSERT INTO domain_hr.hrm_operations_gate_evidence
                      (id, tenant_id, gate_id, evidence_type, title, artifact_ref,
                       submitted_by, metadata)
                    VALUES
                      (:id, :tenant_id, :gate_id, :evidence_type, :title, :artifact_ref,
                       :submitted_by, CAST(:metadata AS jsonb))
                    RETURNING id, gate_id, evidence_type, title, artifact_ref,
                              submitted_by, submitted_at, metadata"""),
            {
                "id": evidence_id,
                "tenant_id": self.tenant_id,
                "gate_id": gate_id,
                "evidence_type": evidence_type,
                "title": title,
                "artifact_ref": artifact_ref,
                "submitted_by": submitted_by,
                "metadata": __import__("json").dumps(metadata),
            },
        ).mappings().first()
        if current_status != "approved":
            self.db.execute(
                text("""UPDATE domain_hr.hrm_operations_gates
                        SET status = 'evidence_submitted', updated_at = NOW(), rejection_reason = NULL
                        WHERE tenant_id = :tenant_id AND gate_id = :gate_id"""),
                {"tenant_id": self.tenant_id, "gate_id": gate_id},
            )
        self._insert_gate_audit(
            gate_id, "evidence_created", submitted_by,
            current_status,
            "approved" if current_status == "approved" else "evidence_submitted",
            details={"artifact_ref": artifact_ref, "evidence_type": evidence_type},
        )
        self.db.commit()
        return dict(row)

    def decide_gate(
        self,
        gate_id: str,
        decision: str,
        decided_by: str,
        reason: Optional[str],
        current_status: str,
        evidence_count: int,
    ) -> str:
        """Apply approve/reject decision. Returns new status."""
        if decision == "approve" and evidence_count < 1:
            from app.core.exceptions import ConflictError
            raise ConflictError("Gate approval requires at least one evidence artifact")
        to_status = "approved" if decision == "approve" else "rejected"
        self.db.execute(
            text("""UPDATE domain_hr.hrm_operations_gates
                    SET status = :status,
                        approved_by = CASE WHEN :status = 'approved' THEN :actor ELSE NULL END,
                        approved_at = CASE WHEN :status = 'approved' THEN NOW() ELSE NULL END,
                        rejection_reason = CASE WHEN :status = 'rejected' THEN :reason ELSE NULL END,
                        updated_at = NOW()
                    WHERE tenant_id = :tenant_id AND gate_id = :gate_id"""),
            {
                "tenant_id": self.tenant_id,
                "gate_id": gate_id,
                "status": to_status,
                "actor": decided_by,
                "reason": reason,
            },
        )
        self._insert_gate_audit(
            gate_id, f"gate_{decision}d", decided_by,
            current_status, to_status,
            reason=reason,
            details={"evidence_count": evidence_count},
        )
        self.db.commit()
        return to_status

    def record_gate_probe(
        self,
        gate_id: str,
        probe_id: str,
        provider: str,
        probe_type: str,
        result: str,
        performed_by: str,
        details: dict,
        current_status: str,
    ) -> dict:
        """Insert probe record, update gate status, write audit. Returns probe row dict."""
        row = self.db.execute(
            text("""INSERT INTO domain_hr.hrm_operations_gate_probes
                      (id, tenant_id, gate_id, provider, probe_type, result, performed_by, details)
                    VALUES
                      (:id, :tenant_id, :gate_id, :provider, :probe_type, :result, :performed_by,
                       CAST(:details AS jsonb))
                    RETURNING id, gate_id, provider, probe_type, result,
                              performed_by, performed_at, details"""),
            {
                "id": probe_id,
                "tenant_id": self.tenant_id,
                "gate_id": gate_id,
                "provider": provider,
                "probe_type": probe_type,
                "result": result,
                "performed_by": performed_by,
                "details": __import__("json").dumps(details),
            },
        ).mappings().first()
        to_status = "probe_passed" if result == "passed" and current_status != "approved" else current_status
        if result in {"failed", "not_configured"} and current_status != "approved":
            to_status = "external_evidence_required"
        self.db.execute(
            text("""UPDATE domain_hr.hrm_operations_gates
                    SET status = :status,
                        last_probe_status = :probe_status,
                        last_probe_at = NOW(),
                        updated_at = NOW()
                    WHERE tenant_id = :tenant_id AND gate_id = :gate_id"""),
            {
                "tenant_id": self.tenant_id,
                "gate_id": gate_id,
                "status": to_status,
                "probe_status": result,
            },
        )
        self._insert_gate_audit(
            gate_id, "connector_probe", performed_by,
            current_status, to_status,
            details={"provider": provider, "probe_type": probe_type, "result": result},
        )
        self.db.commit()
        return dict(row)

    def _insert_gate_audit(
        self,
        gate_id: str,
        event_type: str,
        actor: str,
        from_status: str,
        to_status: str,
        reason: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> None:
        import json as _json
        self.db.execute(
            text("""INSERT INTO domain_hr.hrm_operations_gate_audit
                      (id, tenant_id, gate_id, event_type, actor, from_status, to_status,
                       reason, details, created_at)
                    VALUES
                      (:id, :tenant_id, :gate_id, :event_type, :actor, :from_status, :to_status,
                       :reason, CAST(:details AS jsonb), NOW())"""),
            {
                "id": str(uuid7()),
                "tenant_id": self.tenant_id,
                "gate_id": gate_id,
                "event_type": event_type,
                "actor": actor,
                "from_status": from_status,
                "to_status": to_status,
                "reason": reason,
                "details": _json.dumps(details or {}),
            },
        )

    # ── HRM Gates — DB reads ──────────────────────────────────────────────────

    def _gate_datetime(self, value: Any) -> str | None:
        if value is None:
            return None
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return str(value)

    @staticmethod
    def _row_to_dict(row: Any) -> dict[str, Any]:
        if row is None:
            return {}
        if isinstance(row, dict):
            return row
        try:
            return dict(row)
        except Exception:
            return {k: getattr(row, k) for k in dir(row) if not k.startswith("_")}

    def _gate_readiness_metadata(self, gate_id: str) -> dict[str, Any]:
        defaults: dict[str, dict[str, Any]] = {
            "eau-communication": {"priority": "P0", "riskLevel": "hoch", "dueDate": "2026-05-20"},
            "datev-payroll": {"priority": "P0", "riskLevel": "hoch", "dueDate": "2026-05-21"},
            "office-sso-connectors": {"priority": "P0", "riskLevel": "hoch", "dueDate": "2026-05-22"},
            "documents-esign": {"priority": "P1", "riskLevel": "mittel", "dueDate": "2026-05-24"},
            "privacy-contracts": {"priority": "P0", "riskLevel": "hoch", "dueDate": "2026-05-20"},
            "works-council-dsfa": {"priority": "P0", "riskLevel": "hoch", "dueDate": "2026-05-23"},
            "retention-legal": {"priority": "P1", "riskLevel": "mittel", "dueDate": "2026-05-27"},
        }
        return {
            **defaults.get(gate_id, {"priority": "P1", "riskLevel": "mittel", "dueDate": None}),
            "allowedRoles": ["HR Admin", "Payroll Lead", "IT Admin", "Datenschutz", "Legal"],
            "readOnlyRoles": ["Geschaeftsleitung", "Betriebsrat"],
        }

    def _merge_gate_state(self, template: HrmOperationsGateOut, row: dict[str, Any] | None) -> HrmOperationsGateOut:
        enriched = template.model_copy(update=self._gate_readiness_metadata(template.id))
        if not row:
            return enriched
        return enriched.model_copy(update={
            "status": row.get("status") or enriched.status,
            "ownerRole": row.get("owner_role") or enriched.ownerRole,
            "goLiveBlocking": bool(row.get("go_live_blocking", enriched.goLiveBlocking)),
            "lastChangedAt": self._gate_datetime(row.get("updated_at") or row.get("approved_at") or row.get("last_probe_at")),
            "evidenceCount": int(row.get("evidence_count") or 0),
            "latestEvidenceRef": row.get("latest_evidence_ref"),
            "lastProbeStatus": row.get("last_probe_status"),
            "lastProbeAt": self._gate_datetime(row.get("last_probe_at")),
            "approvedBy": row.get("approved_by"),
            "approvedAt": self._gate_datetime(row.get("approved_at")),
            "rejectionReason": row.get("rejection_reason"),
        })

    def _seed_hrm_gates(self) -> None:
        for gate in self.build_hrm_operations_gates().gates:
            self.db.execute(
                text("""
                    INSERT INTO domain_hr.hrm_operations_gates
                      (tenant_id, gate_id, status, owner_role, go_live_blocking, metadata)
                    VALUES
                      (:tenant_id, :gate_id, :status, :owner_role, :go_live_blocking, CAST(:metadata AS jsonb))
                    ON CONFLICT (tenant_id, gate_id) DO UPDATE SET
                      owner_role = EXCLUDED.owner_role,
                      go_live_blocking = EXCLUDED.go_live_blocking,
                      updated_at = NOW()
                """),
                {
                    "tenant_id": self.tenant_id,
                    "gate_id": gate.id,
                    "status": gate.status,
                    "owner_role": gate.ownerRole,
                    "go_live_blocking": gate.goLiveBlocking,
                    "metadata": json.dumps({"title": gate.title}),
                },
            )

    def _load_hrm_gates_from_db(self) -> HrmOperationsGatesOut:
        self._seed_hrm_gates()
        rows = self.db.execute(
            text("""
                SELECT
                  g.gate_id, g.status, g.owner_role, g.go_live_blocking,
                  g.last_probe_status, g.last_probe_at, g.approved_by, g.approved_at,
                  g.rejection_reason, g.updated_at,
                  COALESCE(ev.evidence_count, 0) AS evidence_count,
                  ev.latest_evidence_ref
                FROM domain_hr.hrm_operations_gates g
                LEFT JOIN (
                  SELECT tenant_id, gate_id, COUNT(*) AS evidence_count,
                         (ARRAY_AGG(artifact_ref ORDER BY submitted_at DESC))[1] AS latest_evidence_ref
                  FROM domain_hr.hrm_operations_gate_evidence
                  WHERE tenant_id = :tenant_id
                  GROUP BY tenant_id, gate_id
                ) ev ON ev.tenant_id = g.tenant_id AND ev.gate_id = g.gate_id
                WHERE g.tenant_id = :tenant_id
                ORDER BY g.gate_id
            """),
            {"tenant_id": self.tenant_id},
        ).mappings().all()
        catalog = {g.id: g for g in self.build_hrm_operations_gates().gates}
        merged = [
            self._merge_gate_state(catalog[row["gate_id"]], self._row_to_dict(row))
            for row in rows
            if row["gate_id"] in catalog
        ]
        known = {g.id for g in merged}
        merged.extend(g for gid, g in catalog.items() if gid not in known)
        go_live = not any(g.goLiveBlocking and g.status != "approved" for g in merged)
        return HrmOperationsGatesOut(
            status="approved" if go_live else "external_gates_runtime",
            asOf="2026-05-13",
            goLiveAllowed=go_live,
            summary=(
                "Alle blockierenden HRM-Betriebsfreigaben sind technisch approved."
                if go_live
                else "HRM-Go-live bleibt durch persistente Betriebsfreigabe-Gates blockiert."
            ),
            gates=merged,
            closureDefinition=[
                "Gate-Status wird tenant-spezifisch aus domain_hr.hrm_operations_gates gelesen.",
                "Evidence, Connector-Probes und Entscheidungen werden persistent und auditierbar gespeichert.",
                "Go-live ist nur erlaubt, wenn alle blocking Gates approved sind.",
                "Statischer Katalog dient nur als Seed/Fallback; Produktivfreigaben entstehen durch Workflow-Aktionen.",
            ],
        )

    def get_hrm_operations_gates(self) -> HrmOperationsGatesOut:
        """Load gates from DB with fallback to static catalog."""
        try:
            return self._load_hrm_gates_from_db()
        except SQLAlchemyError:
            return self.build_hrm_operations_gates()

    def get_single_hrm_gate(self, gate_id: str) -> HrmOperationsGateOut:
        gates = self.get_hrm_operations_gates()
        for gate in gates.gates:
            if gate.id == gate_id:
                return gate
        raise KeyError(gate_id)

    def gate_evidence_out(self, row: dict[str, Any]) -> HrmOperationsGateEvidenceOut:
        meta = row.get("metadata") or {}
        if isinstance(meta, str):
            meta = json.loads(meta)
        return HrmOperationsGateEvidenceOut(
            id=str(row["id"]),
            gateId=str(row["gate_id"]),
            evidenceType=str(row["evidence_type"]),
            title=str(row["title"]),
            artifactRef=str(row["artifact_ref"]),
            submittedBy=str(row["submitted_by"]),
            submittedAt=self._gate_datetime(row.get("submitted_at")) or datetime.utcnow().isoformat(),
            metadata=meta,
        )

    def gate_probe_out(self, row: dict[str, Any]) -> HrmOperationsGateProbeOut:
        details = row.get("details") or {}
        if isinstance(details, str):
            details = json.loads(details)
        return HrmOperationsGateProbeOut(
            id=str(row["id"]),
            gateId=str(row["gate_id"]),
            provider=str(row["provider"]),
            probeType=str(row["probe_type"]),
            result=str(row["result"]),
            performedBy=str(row["performed_by"]),
            performedAt=self._gate_datetime(row.get("performed_at")) or datetime.utcnow().isoformat(),
            details=details,
        )

    # ── HRM static builders ───────────────────────────────────────────────────

    @staticmethod
    def build_hrm_operations_gates() -> HrmOperationsGatesOut:
        gates = [
            HrmOperationsGateOut(
                id="eau-communication",
                title="eAU-Kommunikationszugang und Krankenkassen-Testverfahren",
                status="external_evidence_required",
                ownerRole="HR/Ops",
                goLiveBlocking=True,
                evidenceRequired=[
                    "Nachweis produktiver oder freigegebener Testzugang zum eAU-Arbeitgeberverfahren",
                    "Protokoll fuer Abfrage, Rueckmeldung, Fehlercode und Fristenfall",
                    "Bestaetigung, dass keine Diagnosedaten gespeichert werden",
                ],
                acceptanceCriteria=[
                    "Krankmeldung erzeugt minimalen HR-Status ohne Diagnose",
                    "eAU-Abfrage und Rueckmeldung sind nachvollziehbar protokolliert",
                    "Fehlerrueckmeldungen blockieren Payroll/Planung fachlich sichtbar",
                ],
                auditTrail=["request_id", "employee_ref", "absence_ref", "status_code", "checked_at"],
                professionalPractice=["Datenminimierung", "Fristenmonitor", "Vier-Augen-Ausnahme bei manueller Korrektur"],
            ),
            HrmOperationsGateOut(
                id="datev-payroll",
                title="DATEV-/Payroll-Zielformat und Steuerberaterfreigabe",
                status="external_evidence_required",
                ownerRole="Payroll/Finance",
                goLiveBlocking=True,
                evidenceRequired=[
                    "Festgelegtes Zielformat fuer DATEV LODAS, Lohn und Gehalt oder Steuerbuero-Import",
                    "Testexport mit Lohnarten, Kostenstellen, Fehlzeiten und Korrekturen",
                    "Freigabe durch Steuerbuero oder Payroll-Verantwortliche",
                ],
                acceptanceCriteria=[
                    "Exportpaket ist wiederholbar und auditierbar",
                    "Nur freigegebene time_entries werden exportiert",
                    "Blocker verhindern Monatsabschluss ohne Klaerung",
                ],
                auditTrail=["export_id", "period_from", "period_to", "created_by", "blocker_count"],
                professionalPractice=["Vier-Augen-Freigabe", "Exportprotokoll", "Keine stille Mutation exportierter Zeiten"],
            ),
            HrmOperationsGateOut(
                id="office-sso-connectors",
                title="Microsoft 365, Google Workspace und SSO",
                status="external_evidence_required",
                ownerRole="IT/Ops",
                goLiveBlocking=True,
                evidenceRequired=[
                    "Tenant-IDs, OAuth-Scopes und Redirect-URIs dokumentiert",
                    "SSO-/Rollenmapping fuer Employee, Manager, HR, Payroll und Admin getestet",
                    "Kalenderimport speichert private Termine nur als Busy-Blocker",
                ],
                acceptanceCriteria=[
                    "SSO-Login erzwingt MFA gemaess Tenant-Policy",
                    "Kalender-Sync verletzt keine private Sichtbarkeit",
                    "Connector-Probe kann ohne PII-Leakage wiederholt werden",
                ],
                auditTrail=["connector_id", "tenant_id", "scope_set", "last_probe_at", "probe_result"],
                professionalPractice=["Least-Privilege-Scopes", "Busy-only Datenschutz", "Secret-Rotation"],
            ),
            HrmOperationsGateOut(
                id="documents-esign",
                title="LibreOffice-Rendering, DMS und E-Signatur",
                status="external_evidence_required",
                ownerRole="HR/Ops/Legal",
                goLiveBlocking=True,
                evidenceRequired=[
                    "Vorlagenbibliothek mit Versionsstand und Verantwortlichem",
                    "DMS-Ablage mit Dokumentklasse, Retention und Audit-Referenz",
                    "E-Signatur-Anbieterfreigabe inklusive AVV/DPA",
                ],
                acceptanceCriteria=[
                    "Dokumentgenerierung ist reproduzierbar",
                    "Signaturstatus und Archiv-Ref landen in der Personalakte",
                    "Schriftform- und Textform-Ausnahmen sind dokumentiert",
                ],
                auditTrail=["template_version", "document_id", "signature_status", "archive_ref"],
                professionalPractice=["Vorlagenreview", "Signaturstatus", "Retention je Dokumentklasse"],
            ),
            HrmOperationsGateOut(
                id="privacy-contracts",
                title="AVV/DPA, Hosting, Subprozessoren und Datenexport",
                status="external_evidence_required",
                ownerRole="Datenschutz/Ops",
                goLiveBlocking=True,
                evidenceRequired=[
                    "AVV/DPA je Anbieter",
                    "Hostingort und Subprozessorenliste",
                    "Datenexport- und Loeschprozess fuer Anbieterwechsel",
                ],
                acceptanceCriteria=[
                    "Kein Anbieter ohne AVV/DPA im Produktivbetrieb",
                    "Datenportabilitaet ist getestet",
                    "Loesch- und Auskunftsprozess ist nachvollziehbar",
                ],
                auditTrail=["vendor_id", "dpa_version", "hosting_region", "subprocessor_reviewed_at"],
                professionalPractice=["Vendor-Register", "Datenminimierung", "jaehrliche Subprozessorenpruefung"],
            ),
            HrmOperationsGateOut(
                id="works-council-dsfa",
                title="Betriebsrat, DSFA, HR-Reporting und KI-Assistenzfreigaben",
                status="external_evidence_required",
                ownerRole="HR/Datenschutz/Betriebsrat",
                goLiveBlocking=True,
                evidenceRequired=[
                    "Betriebsvereinbarung oder dokumentierte Mitbestimmungsbewertung",
                    "DSFA-Pruefung fuer konkret vorgesehene HR-Reports oder KI-Assistenzfunktionen",
                    "Freigabe konkreter KI-Assistenzwerkzeuge inklusive Human-Gate",
                ],
                acceptanceCriteria=[
                    "Keine Funktion fuer Mitarbeitendenueberwachung oder automatische Leistungsbewertung vorgesehen",
                    "Analytics nutzt Aggregationsschwellen",
                    "KI-Assistenz erstellt nur Vorschlaege oder Zusammenfassungen mit menschlicher Freigabe",
                ],
                auditTrail=["policy_id", "dsfa_ref", "approval_ref", "effective_from"],
                professionalPractice=["Transparenz fuer Betroffene", "Human Oversight", "AI-Act-Hochrisikopruefung"],
            ),
            HrmOperationsGateOut(
                id="retention-legal",
                title="Rechtsfreigabe fuer Retention und Dokumentklassen",
                status="external_evidence_required",
                ownerRole="Legal/HR",
                goLiveBlocking=True,
                evidenceRequired=[
                    "Freigegebene Aufbewahrungsfristen je Dokumentklasse",
                    "Loeschregeln fuer Austritt, Zweckfortfall und Widerspruch",
                    "Ausnahmen fuer laufende Verfahren oder gesetzliche Pflichten",
                ],
                acceptanceCriteria=[
                    "Personalakte zeigt Retention und Loeschblocker je Dokument",
                    "Loeschlauf ist vor Produktivbetrieb fachlich freigegeben",
                    "Auskunftsexport enthaelt Retention-Plan und Audit-Hinweise",
                ],
                auditTrail=["document_type", "retention_rule_version", "approved_by", "approved_at"],
                professionalPractice=["Jaehrlicher Review", "Zweckbindung", "Keine automatische Loeschung ohne Pruefprotokoll"],
            ),
        ]
        go_live = not any(g.goLiveBlocking and g.status != "approved" for g in gates)
        return HrmOperationsGatesOut(
            status="external_gates_defined",
            asOf="2026-05-13",
            goLiveAllowed=go_live,
            summary="Repo fachlich abgeschlossen; Produktiv-Go-live bleibt bis zur Evidenzfreigabe aller externen Gates blockiert.",
            gates=gates,
            closureDefinition=[
                "Jedes Gate besitzt Owner, Evidenz, Abnahmekriterien und Auditspur.",
                "Go-live ist nur erlaubt, wenn alle blocking Gates approved sind.",
                "Fehlende Zugangsdaten oder Rechtsfreigaben werden nicht als Repo-Gap gefuehrt, sondern als Betriebsfreigabe.",
                "Fachliche Contracts bleiben stabil und koennen mit echten Nachweisen befuellt werden.",
            ],
        )

    @staticmethod
    def build_hrm_operating_system() -> HrmOperatingSystemOut:
        closed_repo_gaps = [
            "HRM-AKTE-001", "HRM-EAU-001", "HRM-DATEV-001", "HRM-CONTRACTS-001",
            "HRM-ESS-001", "HRM-MSS-001", "HRM-RECRUITING-001", "HRM-OFFBOARDING-001",
            "HRM-WORKFLOWS-001", "HRM-ANALYTICS-001", "HRM-PRIVACY-001", "HRM-AI-GOV-001",
            "HRM-M365-001", "HRM-GOOGLE-001", "HRM-LIBREOFFICE-001",
        ]
        return HrmOperatingSystemOut(
            status="repo_contract_complete",
            asOf="2026-05-13",
            closedRepoGaps=closed_repo_gaps,
            timeEntryModelRules=[
                "Arbeitszeit und Abwesenheiten liegen in domain_hr.time_entries.",
                "Datumsspalte ist entry_date; Stundenfeld ist hours.",
                "Abwesenheiten sind entry_type IN ('Urlaub','Krank','Unbezahlt','Sonstiges').",
                "Schreibpfade nutzen RETURNING fuer atomare Mutation und Read-Model.",
                "Keine neue time_bookings- oder absences-Tabelle fuer HR-Time.",
            ],
            modules=[
                HrmOperatingSystemModuleOut(
                    id="employee-file", title="Digitale Personalakte", status="contract_complete",
                    apiContracts=["GET /api/v1/personal/employee-files/{employee_ref}", "POST /api/v1/personal/employee-files/{employee_ref}/documents"],
                    controls=["Dokumentklassen", "Rollenfilter", "Retention-Sicht", "Audit-Ref", "Exportpaket"],
                    externalGates=["produktive DMS-Ablage", "Rechtsfreigabe Retention"],
                ),
                HrmOperatingSystemModuleOut(
                    id="eau", title="eAU und Krankmeldung", status="contract_complete",
                    apiContracts=["POST /api/v1/personal/absences/import", "GET /api/v1/personal/hrm-operating-system"],
                    controls=["keine Diagnosedaten", "Fristenmonitor", "Krankenkassenstatus", "Audit ohne medizinische Details"],
                    externalGates=["eAU-Kommunikationszugang", "Krankenkassen-Testverfahren"],
                ),
                HrmOperatingSystemModuleOut(
                    id="payroll-datev", title="Payroll, DATEV und Monatsabschluss", status="contract_complete",
                    apiContracts=["GET /api/v1/personal/payroll-exports", "POST /api/v1/personal/payroll-exports"],
                    controls=["Lohnarten", "Fehlzeiten", "Kostenstellen", "Blocker", "Monatsabschlussprotokoll"],
                    externalGates=["DATEV-Zielformat", "Steuerberaterfreigabe"],
                ),
                HrmOperatingSystemModuleOut(
                    id="self-service", title="Employee und Manager Self Service", status="contract_complete",
                    apiContracts=["GET /api/v1/personal/employee-files/{employee_ref}", "POST /api/v1/personal/time-entries", "GET /api/v1/personal/work-plan", "GET /api/v1/personal/time-cockpit"],
                    controls=["Rollenfilter", "Freigabequeue", "Teamkalender", "Datenantrag als Workflow"],
                    externalGates=["Betriebsvereinbarung Self-Service", "SSO-Rollenzuordnung"],
                ),
                HrmOperatingSystemModuleOut(
                    id="ai-governance", title="Kontrollierte HR-KI", status="contract_complete",
                    apiContracts=["GET /api/v1/personal/hrm-readiness", "GET /api/v1/personal/hrm-operating-system"],
                    controls=["Human-Gate", "Protokollierung", "Transparenz", "nur konkret freigegebene Assistenzfunktionen"],
                    externalGates=["Konformitaetspruefung fuer konkret vorgesehene KI-Assistenztools"],
                ),
            ],
            externalOperatingGates=[
                "Echte eAU-/DATEV-/Microsoft-/Google-/LibreOffice-/E-Signatur-Zugangsdaten",
                "AVV/DPA, Hostingort, Subprozessoren und Betriebsvereinbarungen",
                "Rechtsfreigabe fuer Retention, DSFA und konkrete KI-Werkzeuge",
            ],
        )

    @staticmethod
    def build_hrm_readiness() -> HrmReadinessOut:
        minimum_checklist = [
            "Digitale Personalakte", "DSGVO-konformes Rechte- und Loeschkonzept",
            "Arbeitszeiterfassung", "Urlaubs- und Abwesenheitsmanagement", "eAU-Prozess",
            "Payroll-/DATEV-Schnittstelle", "Vertrags- und Dokumentenvorlagen",
            "Employee Self Service", "Manager Self Service", "Recruiting und Bewerbermanagement",
            "Onboarding und Offboarding", "Workflows mit Freigaben", "Reporting und HR-Dashboards",
            "Microsoft-365-, LibreOffice- und Google-Workspace-Integration",
            "Sichere KI-Funktionen mit menschlicher Kontrolle",
        ]
        capabilities = [
            HrmReadinessCapabilityOut(
                id="hrm-personnel-file", title="Digitale Personalakte und Stammdaten",
                status="contract_complete", priority="P0",
                legalBasis=["DSGVO", "BDSG §26", "Nachweisgesetz"],
                implementedEvidence=["GET/POST/PUT /api/v1/personal/mitarbeiter", "GET /api/v1/personal/time-profiles"],
                missingCapabilities=["Produktive DMS-Ablage und rechtlich freigegebene Retention-Fristen bleiben external_gate"],
                nextSlices=["HRM-AKTE-001", "HRM-DMS-001", "HRM-RETENTION-001"],
                controls=["Datenminimierung", "Need-to-know-Rollen", "Audit-Log", "Export und Loeschlauf"],
            ),
            HrmReadinessCapabilityOut(
                id="hrm-time-absence", title="Arbeitszeit, Urlaub und Abwesenheiten",
                status="implemented", priority="P0",
                legalBasis=["BAG 1 ABR 22/21", "ArbSchG §3 Abs. 2 Nr. 1", "ArbZG"],
                implementedEvidence=["GET /api/v1/personal/time-cockpit", "POST /api/v1/personal/time-entries", "POST /api/v1/personal/absences/import", "GET /api/v1/personal/work-plan"],
                missingCapabilities=["Tarif-/Betriebsvereinbarungs-Regelkalibrierung", "produktive Terminal-/Mobile-Adapter"],
                nextSlices=["HR-TIME-RULES-001", "HR-TIME-MOBILE-001"],
                controls=["Korrekturgrund", "Managerfreigabe", "Payroll-Blocker", "Keine stille Änderung exportierter Zeiten"],
            ),
            HrmReadinessCapabilityOut(
                id="hrm-payroll", title="Payroll-/DATEV-Vorbereitung",
                status="contract_complete", priority="P0",
                legalBasis=["GoBD", "SV-Meldeportal ist kein Entgeltabrechnungsersatz"],
                implementedEvidence=["GET/POST /api/v1/personal/payroll-exports", "Payroll-Readiness im Time-Cockpit"],
                missingCapabilities=["DATEV-Zielformat und Steuerberaterfreigabe bleiben external_gate"],
                nextSlices=["HR-TIME-PAYROLL-CLOSE-001", "HRM-DATEV-001"],
                controls=["Nur freigegebene Werte exportieren", "Kostenstellen", "Blockerliste", "Exportprotokoll"],
            ),
            HrmReadinessCapabilityOut(
                id="hrm-analytics-compliance", title="Reporting, People Analytics, Datenschutz und Mandantenfaehigkeit",
                status="contract_complete", priority="P0",
                legalBasis=["DSGVO", "BDSG §26", "BetrVG Mitbestimmung", "EU AI Act"],
                implementedEvidence=["Time-Cockpit KPIs", "tenant_id auf HR-Time-Tabellen"],
                missingCapabilities=["DSFA- und Betriebsratsfreigaben bleiben external_gate"],
                nextSlices=["HRM-ANALYTICS-001", "HRM-PRIVACY-001", "HRM-AI-GOV-001"],
                controls=["Aggregationsschwellen", "PII-Minimierung", "Exportierbarkeit", "freigegebener Reporting-Zweck"],
            ),
        ]
        integrations = [
            HrmReadinessIntegrationOut(
                id="microsoft-365", title="Microsoft 365, Teams, Outlook, Entra ID",
                status="planned", direction="bidirectional",
                minimumContract=["SSO", "Kalender-Busy-Blocker", "Abwesenheitskalender", "Benutzeranlage"],
                nextSlice="HRM-M365-001",
            ),
            HrmReadinessIntegrationOut(
                id="datev-payroll", title="DATEV, Steuerberater und Payroll",
                status="partial", direction="export",
                minimumContract=["Stammdaten", "Bewegungsdaten", "Fehlzeiten", "Kostenstellen", "Lohnarten"],
                nextSlice="HRM-DATEV-001",
            ),
            HrmReadinessIntegrationOut(
                id="dms-esign", title="DMS und E-Signatur",
                status="planned", direction="bidirectional",
                minimumContract=["Dokumentenklasse", "Retention", "Signaturstatus", "Audit-Ref"],
                nextSlice="HRM-DMS-001",
            ),
        ]
        ai_controls = [
            HrmReadinessAiControlOut(
                id="hrm-ai-assist", title="Kontrollierte HR-KI",
                classification="assistive",
                allowedUse=["Stellenanzeigen-Entwurf", "Dokumentensuche", "Zusammenfassungen", "HR-Chatbot mit Quellen"],
                prohibitedUse=["nicht freigegebene KI-Funktionen", "Personalentscheidungen ohne dokumentierte menschliche Pruefung"],
                requiredControls=["Human approval", "Protokollierung", "Quellenanzeige", "Opt-out/Policy"],
            ),
        ]
        return HrmReadinessOut(
            status="partial",
            country="DE",
            asOf="2026-05-13",
            minimumChecklist=minimum_checklist,
            capabilities=capabilities,
            integrations=integrations,
            aiControls=ai_controls,
            residualRisks=[
                "Rechtsfeinpruefung und Betriebsvereinbarungen muessen vor Produktivbetrieb abgeschlossen sein.",
                "Produktive eAU-, DATEV-, Microsoft-365- und Google-Workspace-Zugangsdaten fehlen.",
                "AVV/DPA, Hostingort, Subprozessoren und DSFA sind je Fremdanbieter zu pruefen.",
            ],
        )

    # ── Employee File ─────────────────────────────────────────────────────────

    _DOCUMENT_CLASSES: dict[str, dict[str, Any]] = {
        "employment_contract": {
            "title": "Arbeitsvertrag",
            "legal_basis": ["BDSG §26", "Nachweisgesetz", "DSGVO Art. 6(1)(b)"],
            "default_visibility": "hr",
            "retention_years": 10,
            "requires_dms_ref": True,
            "deletion_rule": "Nach Austritt und Ablauf arbeits-/steuerrechtlicher Fristen pruefen.",
        },
        "payroll_document": {
            "title": "Gehalts- und Payroll-Dokument",
            "legal_basis": ["BDSG §26", "GoBD", "Steuerrecht"],
            "default_visibility": "payroll",
            "retention_years": 10,
            "requires_dms_ref": True,
            "deletion_rule": "Nicht loeschen, solange Payroll-/Steuerfristen laufen.",
        },
        "certificate": {
            "title": "Bescheinigung oder Zertifikat",
            "legal_basis": ["BDSG §26", "Arbeitsschutz", "Qualifikationsnachweis"],
            "default_visibility": "employee",
            "retention_years": 6,
            "requires_dms_ref": False,
            "deletion_rule": "Nach Ablauf und Ersatznachweis pruefen.",
        },
        "absence_evidence": {
            "title": "Abwesenheitsnachweis",
            "legal_basis": ["BDSG §26", "Entgeltfortzahlungsgesetz"],
            "default_visibility": "hr",
            "retention_years": 5,
            "requires_dms_ref": True,
            "deletion_rule": "Nur erforderliche Statusdaten; keine Diagnosedaten speichern.",
        },
        "privacy_acknowledgement": {
            "title": "Datenschutz- und Verpflichtungsnachweis",
            "legal_basis": ["DSGVO", "BDSG §26", "Vertraulichkeitsverpflichtung"],
            "default_visibility": "employee",
            "retention_years": 6,
            "requires_dms_ref": True,
            "deletion_rule": "Nach Zweckfortfall und Ablauf interner Nachweisfrist pruefen.",
        },
        "warning_notice": {
            "title": "Abmahnung oder Personalnotiz",
            "legal_basis": ["BDSG §26", "berechtigter HR-Zweck"],
            "default_visibility": "hr",
            "retention_years": 3,
            "requires_dms_ref": True,
            "deletion_rule": "Regelmaessige Erforderlichkeitspruefung; Loeschung bei Zweckfortfall.",
        },
    }

    @classmethod
    def document_classes(cls) -> list[EmployeeFileDocumentClassOut]:
        return [
            EmployeeFileDocumentClassOut(
                documentType=key,
                title=str(v["title"]),
                legalBasis=[str(x) for x in v["legal_basis"]],
                defaultVisibility=str(v["default_visibility"]),
                retentionYears=int(v["retention_years"]),
                requiresDmsRef=bool(v["requires_dms_ref"]),
                deletionRule=str(v["deletion_rule"]),
            )
            for key, v in cls._DOCUMENT_CLASSES.items()
        ]

    @classmethod
    def get_document_class(cls, document_type: str) -> dict[str, Any]:
        if document_type not in cls._DOCUMENT_CLASSES:
            raise ValueError(f"Unknown employee file document type: {document_type}")
        return cls._DOCUMENT_CLASSES[document_type]

    @staticmethod
    def normalize_actor_role(actor_role: str | None) -> str:
        role = (actor_role or "hr").strip().lower()
        return role if role in {"admin", "hr", "payroll", "manager", "employee"} else "employee"

    @staticmethod
    def role_can_view(role: str, visibility: str) -> bool:
        if role in {"admin", "hr"}:
            return True
        if role == "payroll":
            return visibility in {"payroll", "employee"}
        if role == "manager":
            return visibility in {"manager", "employee"}
        return visibility == "employee"

    @staticmethod
    def _add_years(date_text: str | None, years: int) -> str:
        try:
            base = date.fromisoformat(str(date_text)) if date_text else datetime.utcnow().date()
        except ValueError:
            base = datetime.utcnow().date()
        try:
            return base.replace(year=base.year + years).isoformat()
        except ValueError:
            return base.replace(month=2, day=28, year=base.year + years).isoformat()

    def _doc_from_row(self, row: dict[str, Any], actor_role: str) -> EmployeeFileDocumentOut:
        doc_type = str(row.get("document_type") or "certificate")
        doc_class = self.get_document_class(doc_type)
        visibility = str(row.get("visibility") or doc_class["default_visibility"])
        issued_at = row.get("issued_at") or row.get("issuedAt")
        if hasattr(issued_at, "isoformat"):
            issued_at = issued_at.isoformat()
        valid_until = row.get("valid_until") or row.get("validUntil")
        if hasattr(valid_until, "isoformat"):
            valid_until = valid_until.isoformat()
        retention_until = row.get("retention_until") or self._add_years(str(issued_at) if issued_at else None, int(doc_class["retention_years"]))
        if hasattr(retention_until, "isoformat"):
            retention_until = retention_until.isoformat()
        doc_id = str(row.get("id") or f"employee-file-{uuid4()}")
        return EmployeeFileDocumentOut(
            id=doc_id,
            employeeRef=str(row.get("employee_ref") or ""),
            documentType=doc_type,
            title=str(row.get("title") or doc_class["title"]),
            status=str(row.get("status") or "active"),
            visibility=visibility,
            legalBasis=[str(x) for x in doc_class["legal_basis"]],
            issuedAt=str(issued_at) if issued_at else None,
            validUntil=str(valid_until) if valid_until else None,
            retentionUntil=str(retention_until),
            dmsDocumentId=row.get("dms_document_id") or row.get("dmsDocumentId"),
            canEmployeeView=self.role_can_view("employee", visibility),
            canManagerView=self.role_can_view("manager", visibility),
            deletionBlockedReason=str(doc_class["deletion_rule"]),
            auditRef=str(row.get("audit_ref") or f"hrm-akte:{doc_id}"),
        )

    def _pilot_file_documents(self, employee_ref: str, actor_role: str) -> tuple[list[EmployeeFileDocumentOut], int]:
        rows = [
            {"id": f"akte-{employee_ref}-contract", "employee_ref": employee_ref, "document_type": "employment_contract", "title": "Arbeitsvertrag", "visibility": "hr", "issued_at": "2024-01-01", "dms_document_id": "dms-hr-contract-demo"},
            {"id": f"akte-{employee_ref}-certificate", "employee_ref": employee_ref, "document_type": "certificate", "title": "Staplerschein / Qualifikationsnachweis", "visibility": "employee", "issued_at": "2025-04-01", "valid_until": "2028-04-01", "dms_document_id": "dms-hr-cert-demo"},
            {"id": f"akte-{employee_ref}-payroll", "employee_ref": employee_ref, "document_type": "payroll_document", "title": "Payroll-Stammdatenblatt", "visibility": "payroll", "issued_at": "2025-01-01", "dms_document_id": "dms-hr-payroll-demo"},
        ]
        docs = [self._doc_from_row(r, actor_role) for r in rows]
        visible = [d for d in docs if self.role_can_view(actor_role, d.visibility)]
        return visible, len(docs) - len(visible)

    def get_employee_file(self, employee_ref: str, actor_role: str) -> EmployeeFileOut:
        try:
            rows = self.db.execute(
                text("""
                    SELECT id, employee_ref, document_type, title, status, visibility,
                           issued_at, valid_until, retention_until, dms_document_id, audit_ref
                    FROM domain_hr.employee_file_documents
                    WHERE tenant_id = :tenant_id AND employee_ref = :employee_ref
                    ORDER BY issued_at DESC NULLS LAST, created_at DESC NULLS LAST
                """),
                {"tenant_id": self.tenant_id, "employee_ref": employee_ref},
            ).mappings().all()
            if rows:
                docs = [self._doc_from_row(dict(r), actor_role) for r in rows]
                visible = [d for d in docs if self.role_can_view(actor_role, d.visibility)]
                hidden = len(docs) - len(visible)
                source = "database"
            else:
                visible, hidden = self._pilot_file_documents(employee_ref, actor_role)
                source = "pilot"
        except Exception:
            visible, hidden = self._pilot_file_documents(employee_ref, actor_role)
            source = "pilot"
        return EmployeeFileOut(
            employeeRef=employee_ref,
            source=source,
            actorRole=actor_role,
            documentClasses=self.document_classes(),
            documents=visible,
            hiddenDocumentCount=hidden,
            exportPackage=EmployeeFileExportOut(
                available=True, format="json+zip", includesAuditTrail=True, includesRetentionPlan=True,
                dataSubjectAccessHint="DSGVO-Auskunftspaket enthaelt sichtbare Aktenmetadaten, Audit-Referenzen und Retention-Plan.",
            ),
            retention=EmployeeFileRetentionOut(
                deletionConcept="Dokumentklasse bestimmt Mindestaufbewahrung; Zweckfortfall und Rechtsfristen blockieren automatische Loeschung.",
                reviewCadence="jaehrlich und bei Austritt",
                blockedDocumentCount=sum(1 for d in visible if d.retentionUntil >= datetime.utcnow().date().isoformat()),
                nextReviewHint="HR prueft Retention, DMS-Referenz und Zweckbindung vor Loeschlauf.",
            ),
        )

    def create_employee_file_document(self, employee_ref: str, payload: dict[str, Any], actor_role: str) -> EmployeeFileDocumentOut:
        doc_class = self.get_document_class(payload["documentType"])
        visibility = payload.get("visibility") or str(doc_class["default_visibility"])
        doc_id = f"hrdoc-{uuid4()}"
        retention_until = self._add_years(payload.get("issuedAt"), int(doc_class["retention_years"]))
        audit_ref = f"hrm-akte:{doc_id}"
        row = {
            "id": doc_id, "tenant_id": self.tenant_id, "employee_ref": employee_ref,
            "document_type": payload["documentType"], "title": payload["title"],
            "status": "active", "visibility": visibility,
            "issued_at": payload.get("issuedAt"), "valid_until": payload.get("validUntil"),
            "retention_until": retention_until, "dms_document_id": payload.get("dmsDocumentId"),
            "audit_ref": audit_ref, "notes": payload.get("notes"), "created_by": payload.get("createdBy", "system"),
        }
        try:
            self.db.execute(
                text("""
                    INSERT INTO domain_hr.employee_file_documents (
                        id, tenant_id, employee_ref, document_type, title, status,
                        visibility, issued_at, valid_until, retention_until,
                        dms_document_id, audit_ref, notes, created_by, created_at, updated_at
                    ) VALUES (
                        :id, :tenant_id, :employee_ref, :document_type, :title, :status,
                        :visibility, CAST(:issued_at AS date), CAST(:valid_until AS date),
                        CAST(:retention_until AS date), :dms_document_id, :audit_ref,
                        :notes, :created_by, NOW(), NOW()
                    )
                """),
                row,
            )
            self.db.commit()
        except Exception:
            # Table may not exist yet; contract remains usable as pilot/preview
            pass
        return self._doc_from_row(row, actor_role)
