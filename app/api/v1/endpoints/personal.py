"""Personal endpoints for employee list, time entries and timesheets."""

from __future__ import annotations

import json
from datetime import date, datetime, time
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


class TimeEntryBookingCreateIn(BaseModel):
    employeeRef: str = Field(..., min_length=1, max_length=120)
    datum: str
    startTime: str | None = None
    endTime: str | None = None
    hours: float = Field(..., ge=0)
    entryType: str = Field(default="Arbeit", max_length=40)
    source: str = Field(default="manual", max_length=40)
    costCenter: str | None = Field(default=None, max_length=80)
    workArea: str | None = Field(default=None, max_length=120)
    notes: str | None = Field(default=None, max_length=500)


class TimeEntryBookingCorrectionIn(BaseModel):
    hours: float = Field(..., ge=0)
    correctionReason: str = Field(..., min_length=3, max_length=500)
    startTime: str | None = None
    endTime: str | None = None
    entryType: str = Field(default="Arbeit", max_length=40)
    costCenter: str | None = Field(default=None, max_length=80)
    workArea: str | None = Field(default=None, max_length=120)
    notes: str | None = Field(default=None, max_length=500)


class TimeEntryApproveIn(BaseModel):
    approvedBy: str = Field(..., min_length=1, max_length=120)


class TimeEntryBookingOut(BaseModel):
    id: str
    employeeRef: str
    datum: str
    startTime: str | None = None
    endTime: str | None = None
    hours: float
    entryType: str
    source: str
    status: str
    costCenter: str | None = None
    workArea: str | None = None
    correctionReason: str | None = None
    approvedBy: str | None = None
    approvedAt: str | None = None
    auditRef: str | None = None


class TimeEntryActionOut(BaseModel):
    ok: bool
    entry: TimeEntryBookingOut


class AbsenceImportIn(BaseModel):
    employeeRef: str = Field(..., min_length=1, max_length=120)
    absenceType: str = Field(default="Urlaub", pattern="^(Urlaub|Krank|Unbezahlt|Sonstiges)$")
    fromDate: str
    toDate: str
    status: str = Field(default="Approved", pattern="^(Draft|Submitted|Approved|Rejected|Genehmigt)$")
    sourceSystem: str = Field(default="urlaubsverwaltung", max_length=80)
    externalRef: str | None = Field(default=None, max_length=120)
    note: str | None = Field(default=None, max_length=500)


class AbsenceOut(BaseModel):
    id: str
    employeeRef: str
    datum: str
    absenceType: str
    status: str
    source: str
    externalRef: str | None = None
    planningBlockers: list[str] = Field(default_factory=list)
    note: str | None = None


class AbsenceImportOut(BaseModel):
    ok: bool
    imported: int
    absences: list[AbsenceOut]


class ShiftConflictOut(BaseModel):
    code: str
    severity: str
    message: str
    employeeRef: str | None = None


class ShiftCreateIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=160)
    datum: str
    startTime: str
    endTime: str
    locationCode: str = Field(default="main", max_length=80)
    requiredRole: str = Field(default="employee", max_length=80)
    requiredQualifications: list[str] = Field(default_factory=list)
    requiredHeadcount: int = Field(default=1, ge=1)
    assignedEmployeeRefs: list[str] = Field(default_factory=list)
    notes: str | None = Field(default=None, max_length=500)


class ShiftOut(BaseModel):
    id: str
    datum: str
    name: str
    locationCode: str
    requiredRole: str
    requiredQualifications: list[str] = Field(default_factory=list)
    requiredHeadcount: int
    startTime: str
    endTime: str
    assignedEmployeeRefs: list[str] = Field(default_factory=list)
    status: str
    conflicts: list[ShiftConflictOut] = Field(default_factory=list)
    notes: str | None = None


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


class DriverTimeFindingOut(BaseModel):
    code: str
    severity: str
    message: str
    eventIds: list[str] = Field(default_factory=list)


class DriverTimeEventOut(BaseModel):
    id: str
    fahrer: str
    employeeRef: str
    datum: str
    tour: str | None = None
    fahrzeug: str | None = None
    start: str
    ende: str
    taetigkeit: str
    eventType: str
    quelle: str
    dauer: float
    findings: list[DriverTimeFindingOut] = Field(default_factory=list)


class DriverTimeKpisOut(BaseModel):
    eventCount: int
    fahrerCount: int
    tourCount: int
    vehicleCount: int
    fahrzeitStunden: float
    produktivStunden: float
    ruhezeitStunden: float
    blocker: int
    warnings: int


class DriverTimeSummaryOut(BaseModel):
    datum: str
    source: str
    kpis: DriverTimeKpisOut
    findings: list[DriverTimeFindingOut]
    events: list[DriverTimeEventOut]


class TimeCockpitKpisOut(BaseModel):
    presentEmployees: int
    absentEmployees: int
    pendingApprovals: int
    blockerCount: int
    warningCount: int
    payrollReadyEntries: int
    payrollBlockedEntries: int
    totalHours: float
    overtimeHours: float


class TimeApprovalItemOut(BaseModel):
    id: str
    employeeRef: str
    datum: str
    hours: float
    entryType: str
    status: str
    source: str
    risk: str
    nextAction: str


class TimeComplianceIssueOut(BaseModel):
    code: str
    severity: str
    employeeRef: str
    datum: str
    message: str
    sourceId: str | None = None


class TimePayrollReadinessOut(BaseModel):
    status: str
    readyEntries: int
    blockedEntries: int
    blockers: list[str] = Field(default_factory=list)
    exportHint: str


class TimeCockpitOut(BaseModel):
    datum: str
    source: str
    kpis: TimeCockpitKpisOut
    approvalQueue: list[TimeApprovalItemOut]
    complianceIssues: list[TimeComplianceIssueOut]
    payrollReadiness: TimePayrollReadinessOut
    driverTime: DriverTimeSummaryOut


class EmployeeTimeProfileOut(BaseModel):
    employeeRef: str
    displayName: str
    roleCode: str
    roleLabel: str
    locationCode: str
    department: str
    managerRef: str | None = None
    employmentType: str
    weeklyHours: float
    timeModel: str
    costCenter: str | None = None
    payrollGroup: str | None = None
    qualifications: list[str] = Field(default_factory=list)
    canDrive: bool
    driverCardId: str | None = None
    vehicleRefs: list[str] = Field(default_factory=list)
    calendarProvider: str
    status: str


class EmployeeTimeProfileKpisOut(BaseModel):
    employeeCount: int
    driverCount: int
    activeCount: int
    locationCount: int
    qualificationCount: int


class EmployeeTimeProfileCatalogOut(BaseModel):
    source: str
    profiles: list[EmployeeTimeProfileOut]
    kpis: EmployeeTimeProfileKpisOut


_PRODUCTIVE_DRIVER_EVENT_TYPES = {"DRIVING", "LOADING", "UNLOADING", "OTHER_WORK", "AVAILABILITY"}
_REST_DRIVER_EVENT_TYPES = {"BREAK", "DAILY_REST", "WEEKLY_REST"}
_DRIVER_ACTIVITY_LABELS = {
    "DRIVING": "Fahren",
    "LOADING": "Beladen",
    "UNLOADING": "Entladen",
    "OTHER_WORK": "Sonstige Arbeit",
    "AVAILABILITY": "Bereitschaft",
    "BREAK": "Pause",
}
_TACHO_DEVIATION_THRESHOLD_MINUTES = 15
_MINUTES_PER_HOUR = 60
_STANDARD_DAILY_HOURS = 8.0
_LONG_DAY_WARNING_HOURS = 10.0


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


def _to_optional_time_text(value: Any) -> str | None:
    text_value = _to_time_text(value)
    return None if text_value == "-" else text_value


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


def _parse_json_list(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, list):
        return [dict(item) if isinstance(item, dict) else {"value": item} for item in raw]
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except Exception:
            return []
        if isinstance(parsed, list):
            return [dict(item) if isinstance(item, dict) else {"value": item} for item in parsed]
    return []


def _parse_json_string_list(raw: Any) -> list[str]:
    if isinstance(raw, list):
        return [str(item) for item in raw if str(item).strip()]
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except Exception:
            return [raw] if raw.strip() else []
        if isinstance(parsed, list):
            return [str(item) for item in parsed if str(item).strip()]
    return []


def _split_name(full_name: str) -> tuple[str, str]:
    parts = [part for part in full_name.strip().split(" ") if part]
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return " ".join(parts[:-1]), parts[-1]


def _parse_clock_minutes(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, time):
        return value.hour * _MINUTES_PER_HOUR + value.minute
    text_value = str(value).strip()
    if not text_value:
        return None
    try:
        parsed_time = time.fromisoformat(text_value[:8])
    except ValueError:
        return None
    return parsed_time.hour * _MINUTES_PER_HOUR + parsed_time.minute


def _parse_entry_date(value: str) -> date:
    try:
        return datetime.fromisoformat(value).date()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid datum format") from exc


def _date_range(start: date, end: date) -> list[date]:
    if end < start:
        raise HTTPException(status_code=400, detail="toDate must be on or after fromDate")
    days = (end - start).days
    return [date.fromordinal(start.toordinal() + offset) for offset in range(days + 1)]


def _time_booking_from_row(row: Any) -> TimeEntryBookingOut:
    row_map = dict(row)
    return TimeEntryBookingOut(
        id=str(row_map.get("id") or ""),
        employeeRef=str(row_map.get("employee_ref") or ""),
        datum=_to_iso(row_map.get("entry_date")),
        startTime=_to_optional_time_text(row_map.get("start_time")),
        endTime=_to_optional_time_text(row_map.get("end_time")),
        hours=float(row_map.get("hours") or 0),
        entryType=str(row_map.get("entry_type") or "Arbeit"),
        source=str(row_map.get("source") or "manual"),
        status=str(row_map.get("status") or "Draft"),
        costCenter=str(row_map.get("cost_center") or "") or None,
        workArea=str(row_map.get("work_area") or "") or None,
        correctionReason=str(row_map.get("correction_reason") or "") or None,
        approvedBy=str(row_map.get("approved_by") or "") or None,
        approvedAt=_to_iso(row_map.get("approved_at")) if row_map.get("approved_at") else None,
        auditRef=str(row_map.get("audit_ref") or "") or None,
    )


def _absence_blockers(status: str) -> list[str]:
    if status in {"Approved", "Genehmigt"}:
        return ["tour", "shift", "calendar", "payroll"]
    if status == "Submitted":
        return ["planning-review"]
    return []


def _absence_from_row(row: Any) -> AbsenceOut:
    row_map = dict(row)
    status = str(row_map.get("status") or "Draft")
    return AbsenceOut(
        id=str(row_map.get("id") or ""),
        employeeRef=str(row_map.get("employee_ref") or ""),
        datum=_to_iso(row_map.get("entry_date")),
        absenceType=str(row_map.get("entry_type") or "Urlaub"),
        status=status,
        source=str(row_map.get("source") or "absence"),
        externalRef=str(row_map.get("audit_ref") or "") or None,
        planningBlockers=_absence_blockers(status),
        note=str(row_map.get("notes") or "") or None,
    )


def _shift_conflict_from_item(item: Any) -> ShiftConflictOut:
    if isinstance(item, ShiftConflictOut):
        return item
    item_map = dict(item) if isinstance(item, dict) else {}
    return ShiftConflictOut(
        code=str(item_map.get("code") or "UNKNOWN"),
        severity=str(item_map.get("severity") or "warning"),
        message=str(item_map.get("message") or ""),
        employeeRef=str(item_map.get("employeeRef") or item_map.get("employee_ref") or "") or None,
    )


def _shift_from_row(row: Any) -> ShiftOut:
    row_map = dict(row)
    conflicts_raw = row_map.get("conflicts")
    conflicts = [_shift_conflict_from_item(item) for item in _parse_json_list(conflicts_raw)]
    return ShiftOut(
        id=str(row_map.get("id") or ""),
        datum=_to_iso(row_map.get("shift_date")),
        name=str(row_map.get("name") or ""),
        locationCode=str(row_map.get("location_code") or "main"),
        requiredRole=str(row_map.get("required_role") or "employee"),
        requiredQualifications=_parse_json_string_list(row_map.get("required_qualifications")),
        requiredHeadcount=int(row_map.get("required_headcount") or 1),
        startTime=_to_time_text(row_map.get("starts_at")),
        endTime=_to_time_text(row_map.get("ends_at")),
        assignedEmployeeRefs=_parse_json_string_list(row_map.get("assigned_employee_refs")),
        status=str(row_map.get("status") or "planned"),
        conflicts=conflicts,
        notes=str(row_map.get("notes") or "") or None,
    )


def _shift_status(conflicts: list[ShiftConflictOut]) -> str:
    if any(conflict.severity == "blocker" for conflict in conflicts):
        return "blocked"
    if conflicts:
        return "warning"
    return "planned"


def _build_shift_conflicts(
    assigned_employee_refs: list[str],
    required_headcount: int,
    required_qualifications: list[str],
    profile_rows: list[Any],
    absence_rows: list[Any],
) -> list[ShiftConflictOut]:
    conflicts: list[ShiftConflictOut] = []
    profile_by_ref = {str(row.get("employee_ref") or ""): dict(row) for row in [dict(item) for item in profile_rows]}
    absent_refs = {str(dict(row).get("employee_ref") or "") for row in absence_rows}

    if len(assigned_employee_refs) < required_headcount:
        conflicts.append(
            ShiftConflictOut(
                code="UNDERSTAFFED",
                severity="blocker",
                message="Mindestbesetzung ist nicht erreicht.",
            )
        )

    for employee_ref in assigned_employee_refs:
        profile = profile_by_ref.get(employee_ref)
        if not profile:
            conflicts.append(
                ShiftConflictOut(
                    code="PROFILE_MISSING",
                    severity="blocker",
                    message="Mitarbeiter hat kein HR-Time-Profil.",
                    employeeRef=employee_ref,
                )
            )
            continue
        if _normalize_time_profile_status(profile.get("status")) != "active":
            conflicts.append(
                ShiftConflictOut(
                    code="PROFILE_INACTIVE",
                    severity="blocker",
                    message="Mitarbeiter ist nicht aktiv planbar.",
                    employeeRef=employee_ref,
                )
            )
        if employee_ref in absent_refs:
            conflicts.append(
                ShiftConflictOut(
                    code="ABSENCE_COLLISION",
                    severity="blocker",
                    message="Mitarbeiter hat eine genehmigte Abwesenheit.",
                    employeeRef=employee_ref,
                )
            )
        qualifications = set(_parse_json_string_list(profile.get("qualifications")))
        missing = [qualification for qualification in required_qualifications if qualification not in qualifications]
        if missing:
            conflicts.append(
                ShiftConflictOut(
                    code="QUALIFICATION_MISSING",
                    severity="warning",
                    message=f"Erforderliche Qualifikation fehlt: {', '.join(missing)}.",
                    employeeRef=employee_ref,
                )
            )
    return conflicts


def _normalize_time_profile_status(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"active", "inactive", "on_leave"}:
        return normalized
    if normalized == "aktiv":
        return "active"
    if normalized in {"urlaub", "krank"}:
        return "on_leave"
    return "inactive" if normalized in {"inaktiv", "disabled"} else "active"


def _profile_kpis(profiles: list[EmployeeTimeProfileOut]) -> EmployeeTimeProfileKpisOut:
    qualifications = {qualification for profile in profiles for qualification in profile.qualifications}
    return EmployeeTimeProfileKpisOut(
        employeeCount=len(profiles),
        driverCount=sum(1 for profile in profiles if profile.canDrive or profile.timeModel == "driver"),
        activeCount=sum(1 for profile in profiles if profile.status == "active"),
        locationCount=len({profile.locationCode for profile in profiles if profile.locationCode}),
        qualificationCount=len(qualifications),
    )


def _time_profiles_from_rows(rows: list[Any]) -> list[EmployeeTimeProfileOut]:
    profiles: list[EmployeeTimeProfileOut] = []
    for row in rows:
        row_map = dict(row)
        profiles.append(
            EmployeeTimeProfileOut(
                employeeRef=str(row_map.get("employee_ref") or row_map.get("id") or ""),
                displayName=str(row_map.get("display_name") or row_map.get("employee_ref") or ""),
                roleCode=str(row_map.get("role_code") or "employee"),
                roleLabel=str(row_map.get("role_label") or "Mitarbeiter"),
                locationCode=str(row_map.get("location_code") or "main"),
                department=str(row_map.get("department") or "Allgemein"),
                managerRef=str(row_map.get("manager_ref") or "") or None,
                employmentType=str(row_map.get("employment_type") or "full_time"),
                weeklyHours=float(row_map.get("weekly_hours") or 40.0),
                timeModel=str(row_map.get("time_model") or "standard"),
                costCenter=str(row_map.get("cost_center") or "") or None,
                payrollGroup=str(row_map.get("payroll_group") or "") or None,
                qualifications=_parse_json_string_list(row_map.get("qualifications")),
                canDrive=bool(row_map.get("can_drive")),
                driverCardId=str(row_map.get("driver_card_id") or "") or None,
                vehicleRefs=_parse_json_string_list(row_map.get("vehicle_refs")),
                calendarProvider=str(row_map.get("calendar_provider") or "none"),
                status=_normalize_time_profile_status(row_map.get("status")),
            )
        )
    return profiles


def _time_profiles_from_user_rows(rows: list[Any]) -> list[EmployeeTimeProfileOut]:
    profiles: list[EmployeeTimeProfileOut] = []
    for row in rows:
        row_map = dict(row)
        prefs = _parse_preferences(row_map.get("preferences"))
        roles = row_map.get("roles") or []
        role_code = str(roles[0]) if isinstance(roles, list) and roles else str(prefs.get("role_code") or "employee")
        role_lower = role_code.lower()
        first = str(row_map.get("first_name") or "").strip()
        last = str(row_map.get("last_name") or "").strip()
        display_name = f"{first} {last}".strip() or str(row_map.get("username") or row_map.get("email") or row_map.get("id"))
        can_drive = bool(prefs.get("can_drive")) or any(token in role_lower for token in ("fahrer", "driver", "lkw"))
        qualifications = _parse_json_string_list(prefs.get("qualifications"))
        if can_drive and "driver_time" not in qualifications:
            qualifications.append("driver_time")
        profiles.append(
            EmployeeTimeProfileOut(
                employeeRef=str(row_map.get("id") or row_map.get("email") or display_name),
                displayName=display_name,
                roleCode=role_code,
                roleLabel=str(prefs.get("role_label") or role_code.replace("_", " ").title()),
                locationCode=str(prefs.get("location_code") or prefs.get("standort") or "main"),
                department=str(prefs.get("abteilung") or "Allgemein"),
                managerRef=str(prefs.get("manager_ref") or "") or None,
                employmentType=str(prefs.get("employment_type") or "full_time"),
                weeklyHours=float(prefs.get("weekly_hours") or 40.0),
                timeModel=str(prefs.get("time_model") or ("driver" if can_drive else "standard")),
                costCenter=str(prefs.get("cost_center") or "") or None,
                payrollGroup=str(prefs.get("payroll_group") or "") or None,
                qualifications=qualifications,
                canDrive=can_drive,
                driverCardId=str(prefs.get("driver_card_id") or "") or None,
                vehicleRefs=_parse_json_string_list(prefs.get("vehicle_refs")),
                calendarProvider=str(prefs.get("calendar_provider") or "none"),
                status=_normalize_time_profile_status(prefs.get("hr_status") or ("active" if bool(row_map.get("is_active")) else "inactive")),
            )
        )
    return profiles


def _pilot_time_profiles() -> list[EmployeeTimeProfileOut]:
    return [
        EmployeeTimeProfileOut(
            employeeRef="driver-m-krueger",
            displayName="M. Krueger",
            roleCode="lkw_fahrer",
            roleLabel="LKW-Fahrer",
            locationCode="main",
            department="Logistik",
            employmentType="full_time",
            weeklyHours=40.0,
            timeModel="driver",
            costCenter="LOG",
            payrollGroup="stundenlohn",
            qualifications=["ce_license", "driver_time", "tacho_card"],
            canDrive=True,
            driverCardId="D-1001",
            vehicleRefs=["WL-VA 1840"],
            calendarProvider="microsoft365",
            status="active",
        ),
        EmployeeTimeProfileOut(
            employeeRef="warehouse-l-meier",
            displayName="L. Meier",
            roleCode="lager",
            roleLabel="Lager / Verladung",
            locationCode="main",
            department="Lager",
            employmentType="full_time",
            weeklyHours=40.0,
            timeModel="shift",
            costCenter="LAG",
            payrollGroup="stundenlohn",
            qualifications=["forklift"],
            canDrive=False,
            calendarProvider="microsoft365",
            status="active",
        ),
        EmployeeTimeProfileOut(
            employeeRef="field-a-brandt",
            displayName="A. Brandt",
            roleCode="aussendienst",
            roleLabel="Agrarberater Aussendienst",
            locationCode="field-north",
            department="Vertrieb",
            employmentType="full_time",
            weeklyHours=40.0,
            timeModel="field_service",
            costCenter="VER",
            payrollGroup="gehalt",
            qualifications=["plant_protection_advice"],
            canDrive=False,
            calendarProvider="google",
            status="active",
        ),
    ]


def _duration_hours(start: Any, end: Any) -> float:
    start_minutes = _parse_clock_minutes(start)
    end_minutes = _parse_clock_minutes(end)
    if start_minutes is None or end_minutes is None or end_minutes <= start_minutes:
        return 0.0
    return round((end_minutes - start_minutes) / _MINUTES_PER_HOUR, 2)


def _driver_time_pilot_events(target_date: str) -> list[DriverTimeEventOut]:
    return [
        DriverTimeEventOut(
            id=f"pilot-{target_date}-001",
            fahrer="M. Krueger",
            employeeRef="M. Krueger",
            datum=target_date,
            tour="TOUR-2407",
            fahrzeug="WL-VA 1840",
            start="05:45",
            ende="07:55",
            taetigkeit="Fahren",
            eventType="DRIVING",
            quelle="Tacho",
            dauer=2.17,
        ),
        DriverTimeEventOut(
            id=f"pilot-{target_date}-002",
            fahrer="M. Krueger",
            employeeRef="M. Krueger",
            datum=target_date,
            tour="TOUR-2407",
            fahrzeug="WL-VA 1840",
            start="07:55",
            ende="09:10",
            taetigkeit="Entladen",
            eventType="UNLOADING",
            quelle="Manuell",
            dauer=1.25,
        ),
        DriverTimeEventOut(
            id=f"pilot-{target_date}-003",
            fahrer="S. Weber",
            employeeRef="S. Weber",
            datum=target_date,
            tour="TOUR-2411",
            fahrzeug=None,
            start="06:20",
            ende="08:00",
            taetigkeit="Fahren",
            eventType="DRIVING",
            quelle="Dispo",
            dauer=1.67,
        ),
        DriverTimeEventOut(
            id=f"pilot-{target_date}-004",
            fahrer="A. Brandt",
            employeeRef="A. Brandt",
            datum=target_date,
            tour="TOUR-2409",
            fahrzeug="WL-VA 1217",
            start="08:00",
            ende="08:45",
            taetigkeit="Pause",
            eventType="BREAK",
            quelle="Manuell",
            dauer=0.75,
        ),
    ]


def _events_from_timesheets(rows: list[Any]) -> list[DriverTimeEventOut]:
    events: list[DriverTimeEventOut] = []
    for row in rows:
        row_map = dict(row)
        target_date = _to_iso(row_map.get("entry_date"))
        fahrer = str(row_map.get("driver_name") or "")
        vehicle = str(row_map.get("vehicle_plate") or "").strip() or None
        for index, tour in enumerate(_parse_json_list(row_map.get("tours")), start=1):
            tour_id = str(tour.get("id") or row_map.get("id") or f"tour-{index}")
            start = _to_time_text(tour.get("start"))
            end = _to_time_text(tour.get("ende") or tour.get("end"))
            duration = _duration_hours(start, end)
            events.append(
                DriverTimeEventOut(
                    id=f"{row_map.get('id')}-{index}",
                    fahrer=fahrer,
                    employeeRef=fahrer,
                    datum=target_date,
                    tour=tour_id,
                    fahrzeug=vehicle,
                    start=start,
                    ende=end,
                    taetigkeit="Fahren",
                    eventType="DRIVING",
                    quelle="Manuell",
                    dauer=duration,
                )
            )
            pause = float(tour.get("pause") or 0)
            if pause > 0 and end != "-":
                events.append(
                    DriverTimeEventOut(
                        id=f"{row_map.get('id')}-{index}-break",
                        fahrer=fahrer,
                        employeeRef=fahrer,
                        datum=target_date,
                        tour=tour_id,
                        fahrzeug=vehicle,
                        start=end,
                        ende=end,
                        taetigkeit="Pause",
                        eventType="BREAK",
                        quelle="Manuell",
                        dauer=round(pause / _MINUTES_PER_HOUR, 2),
                    )
                )
    return events


def _approved_absence_ranges(rows: list[Any]) -> list[tuple[str, str, str]]:
    ranges: list[tuple[str, str, str]] = []
    for row in rows:
        row_map = dict(row)
        entry_type = str(row_map.get("entry_type") or "")
        if entry_type.lower() not in {"urlaub", "krank"}:
            continue
        employee_ref = str(row_map.get("employee_ref") or "")
        entry_date = _to_iso(row_map.get("entry_date"))
        ranges.append((employee_ref, entry_date, entry_date))
    return ranges


def _apply_driver_time_findings(
    events: list[DriverTimeEventOut],
    absence_ranges: list[tuple[str, str, str]],
) -> list[DriverTimeFindingOut]:
    findings: list[DriverTimeFindingOut] = []
    events_by_driver: dict[str, list[DriverTimeEventOut]] = {}
    for event in events:
        event.findings = []
        events_by_driver.setdefault(event.employeeRef, []).append(event)

        if event.eventType in {"DRIVING", "VEHICLE_CHANGE"} and not event.fahrzeug:
            finding = DriverTimeFindingOut(
                code="MISSING_VEHICLE",
                severity="blocker",
                message="Fahr- oder Fahrzeugwechselereignis hat kein Fahrzeug.",
                eventIds=[event.id],
            )
            findings.append(finding)
            event.findings.append(finding)
        if event.eventType not in {"DAILY_REST", "WEEKLY_REST"} and not event.tour:
            finding = DriverTimeFindingOut(
                code="MISSING_TOUR",
                severity="warning",
                message="Fahrerzeitereignis hat keinen Tourbezug.",
                eventIds=[event.id],
            )
            findings.append(finding)
            event.findings.append(finding)
        if any(employee == event.employeeRef and start <= event.datum <= end for employee, start, end in absence_ranges):
            finding = DriverTimeFindingOut(
                code="ABSENCE_COLLISION",
                severity="blocker",
                message="Fahrerzeitereignis kollidiert mit genehmigter Abwesenheit.",
                eventIds=[event.id],
            )
            findings.append(finding)
            event.findings.append(finding)

    for driver_events in events_by_driver.values():
        sorted_events = sorted(driver_events, key=lambda item: (item.datum, item.start, item.ende))
        for previous, current in zip(sorted_events, sorted_events[1:]):
            previous_end = _parse_clock_minutes(previous.ende)
            current_start = _parse_clock_minutes(current.start)
            if previous_end is not None and current_start is not None and previous_end > current_start:
                finding = DriverTimeFindingOut(
                    code="EVENT_OVERLAP",
                    severity="blocker",
                    message="Fahrerzeitereignisse ueberlappen sich.",
                    eventIds=[previous.id, current.id],
                )
                findings.append(finding)
                previous.findings.append(finding)
                current.findings.append(finding)

    manual_by_key = {
        (event.employeeRef, event.eventType): event
        for event in events
        if event.quelle.lower() == "manuell"
    }
    for event in events:
        if event.quelle.lower() != "tacho":
            continue
        manual_event = manual_by_key.get((event.employeeRef, event.eventType))
        if manual_event and abs((event.dauer - manual_event.dauer) * _MINUTES_PER_HOUR) > _TACHO_DEVIATION_THRESHOLD_MINUTES:
            finding = DriverTimeFindingOut(
                code="TACHO_MANUAL_DEVIATION",
                severity="warning",
                message="Manuelle Buchung weicht vom Tacho-Import ab.",
                eventIds=[manual_event.id, event.id],
            )
            findings.append(finding)
            manual_event.findings.append(finding)
            event.findings.append(finding)

    return findings


def _build_driver_time_summary(
    target_date: str,
    events: list[DriverTimeEventOut],
    absence_ranges: list[tuple[str, str, str]] | None = None,
    source: str = "database",
) -> DriverTimeSummaryOut:
    findings = _apply_driver_time_findings(events, absence_ranges or [])
    return DriverTimeSummaryOut(
        datum=target_date,
        source=source,
        findings=findings,
        events=events,
        kpis=DriverTimeKpisOut(
            eventCount=len(events),
            fahrerCount=len({event.employeeRef for event in events}),
            tourCount=len({event.tour for event in events if event.tour}),
            vehicleCount=len({event.fahrzeug for event in events if event.fahrzeug}),
            fahrzeitStunden=round(sum(event.dauer for event in events if event.eventType == "DRIVING"), 2),
            produktivStunden=round(sum(event.dauer for event in events if event.eventType in _PRODUCTIVE_DRIVER_EVENT_TYPES), 2),
            ruhezeitStunden=round(sum(event.dauer for event in events if event.eventType in _REST_DRIVER_EVENT_TYPES), 2),
            blocker=sum(1 for finding in findings if finding.severity == "blocker"),
            warnings=sum(1 for finding in findings if finding.severity == "warning"),
        ),
    )


def _time_rows_to_entries(rows: list[Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for row in rows:
        row_map = dict(row)
        entries.append(
            {
                "id": str(row_map.get("id") or ""),
                "employee_ref": str(row_map.get("employee_ref") or ""),
                "entry_date": _to_iso(row_map.get("entry_date")),
                "start_time": _to_time_text(row_map.get("start_time")),
                "end_time": _to_time_text(row_map.get("end_time")),
                "hours": float(row_map.get("hours") or 0),
                "entry_type": str(row_map.get("entry_type") or "Arbeit"),
                "source": str(row_map.get("source") or "manual"),
                "status": str(row_map.get("status") or "Draft"),
            }
        )
    return entries


def _build_time_compliance_issues(
    entries: list[dict[str, Any]],
    driver_time: DriverTimeSummaryOut,
) -> list[TimeComplianceIssueOut]:
    issues: list[TimeComplianceIssueOut] = []
    for entry in entries:
        hours = float(entry["hours"])
        if entry["entry_type"] == "Arbeit" and hours <= 0:
            issues.append(
                TimeComplianceIssueOut(
                    code="MISSING_HOURS",
                    severity="blocker",
                    employeeRef=str(entry["employee_ref"]),
                    datum=str(entry["entry_date"]),
                    message="Arbeitszeiteintrag hat keine Stunden.",
                    sourceId=str(entry["id"]),
                )
            )
        if hours > _LONG_DAY_WARNING_HOURS:
            issues.append(
                TimeComplianceIssueOut(
                    code="LONG_WORKDAY",
                    severity="warning",
                    employeeRef=str(entry["employee_ref"]),
                    datum=str(entry["entry_date"]),
                    message="Arbeitszeit liegt ueber 10 Stunden und braucht Pruefung.",
                    sourceId=str(entry["id"]),
                )
            )
        if entry["entry_type"] in {"Urlaub", "Krank"} and entry["status"] not in {"Approved", "Genehmigt"}:
            issues.append(
                TimeComplianceIssueOut(
                    code="ABSENCE_NOT_APPROVED",
                    severity="blocker",
                    employeeRef=str(entry["employee_ref"]),
                    datum=str(entry["entry_date"]),
                    message="Abwesenheit ist nicht genehmigt.",
                    sourceId=str(entry["id"]),
                )
            )

    for finding in driver_time.findings:
        severity = "blocker" if finding.severity == "blocker" else "warning"
        event = next((item for item in driver_time.events if item.id in finding.eventIds), None)
        issues.append(
            TimeComplianceIssueOut(
                code=finding.code,
                severity=severity,
                employeeRef=event.employeeRef if event else "",
                datum=event.datum if event else driver_time.datum,
                message=finding.message,
                sourceId=finding.eventIds[0] if finding.eventIds else None,
            )
        )
    return issues


def _build_approval_queue(entries: list[dict[str, Any]], issues: list[TimeComplianceIssueOut]) -> list[TimeApprovalItemOut]:
    blocker_ids = {issue.sourceId for issue in issues if issue.severity == "blocker" and issue.sourceId}
    queue: list[TimeApprovalItemOut] = []
    for entry in entries:
        status = str(entry["status"])
        if status in {"Approved", "Genehmigt"}:
            continue
        entry_id = str(entry["id"])
        has_blocker = entry_id in blocker_ids
        queue.append(
            TimeApprovalItemOut(
                id=entry_id,
                employeeRef=str(entry["employee_ref"]),
                datum=str(entry["entry_date"]),
                hours=float(entry["hours"]),
                entryType=str(entry["entry_type"]),
                status=status,
                source=str(entry["source"]),
                risk="blockiert" if has_blocker else "pruefen",
                nextAction="Befund klaeren" if has_blocker else "Freigeben oder korrigieren",
            )
        )
    return queue


def _build_time_cockpit(
    target_date: str,
    entries: list[dict[str, Any]],
    driver_time: DriverTimeSummaryOut,
    source: str,
) -> TimeCockpitOut:
    issues = _build_time_compliance_issues(entries, driver_time)
    approval_queue = _build_approval_queue(entries, issues)
    blockers = [issue.message for issue in issues if issue.severity == "blocker"]
    approved_entries = [entry for entry in entries if entry["status"] in {"Approved", "Genehmigt"}]
    work_entries = [entry for entry in entries if entry["entry_type"] == "Arbeit"]
    absent_entries = [entry for entry in entries if entry["entry_type"] in {"Urlaub", "Krank"}]
    overtime_hours = sum(max(0.0, float(entry["hours"]) - _STANDARD_DAILY_HOURS) for entry in work_entries)
    payroll_blocked = len(blockers) + len(approval_queue)
    payroll_ready = len(approved_entries)
    return TimeCockpitOut(
        datum=target_date,
        source=source,
        driverTime=driver_time,
        complianceIssues=issues,
        approvalQueue=approval_queue,
        payrollReadiness=TimePayrollReadinessOut(
            status="blocked" if payroll_blocked else "ready",
            readyEntries=payroll_ready,
            blockedEntries=payroll_blocked,
            blockers=blockers,
            exportHint="Payroll-Export blockiert bis Freigaben und Befunde erledigt sind." if payroll_blocked else "Payroll-Export fachlich freigabefaehig.",
        ),
        kpis=TimeCockpitKpisOut(
            presentEmployees=len({entry["employee_ref"] for entry in work_entries}),
            absentEmployees=len({entry["employee_ref"] for entry in absent_entries}),
            pendingApprovals=len(approval_queue),
            blockerCount=sum(1 for issue in issues if issue.severity == "blocker"),
            warningCount=sum(1 for issue in issues if issue.severity == "warning"),
            payrollReadyEntries=payroll_ready,
            payrollBlockedEntries=payroll_blocked,
            totalHours=round(sum(float(entry["hours"]) for entry in entries) + driver_time.kpis.produktivStunden, 2),
            overtimeHours=round(overtime_hours, 2),
        ),
    )


def _pilot_time_entries(target_date: str) -> list[dict[str, Any]]:
    return [
        {
            "id": f"pilot-time-{target_date}-001",
            "employee_ref": "L. Meier",
            "entry_date": target_date,
            "start_time": "07:00",
            "end_time": "16:00",
            "hours": 8.0,
            "entry_type": "Arbeit",
            "source": "terminal",
            "status": "Approved",
        },
        {
            "id": f"pilot-time-{target_date}-002",
            "employee_ref": "S. Weber",
            "entry_date": target_date,
            "start_time": "06:20",
            "end_time": "18:05",
            "hours": 11.75,
            "entry_type": "Arbeit",
            "source": "driver-time",
            "status": "Draft",
        },
        {
            "id": f"pilot-time-{target_date}-003",
            "employee_ref": "A. Brandt",
            "entry_date": target_date,
            "start_time": "-",
            "end_time": "-",
            "hours": 0.0,
            "entry_type": "Urlaub",
            "source": "absence",
            "status": "Approved",
        },
    ]


@router.get("/time-profiles", response_model=EmployeeTimeProfileCatalogOut)
async def list_time_profiles(
    status: str | None = Query(default=None),
    role: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    params: dict[str, Any] = {"tenant_id": tenant_id}
    where = ["tenant_id = :tenant_id"]
    if status:
        params["status"] = _normalize_time_profile_status(status)
        where.append("status = :status")
    if role:
        params["role"] = role
        where.append("role_code = :role")

    try:
        rows = db.execute(
            text(
                f"""
                SELECT employee_ref, display_name, role_code, role_label, location_code,
                       department, manager_ref, employment_type, weekly_hours, time_model,
                       cost_center, payroll_group, qualifications, can_drive, driver_card_id,
                       vehicle_refs, calendar_provider, status
                FROM domain_hr.employee_time_profiles
                WHERE {' AND '.join(where)}
                ORDER BY location_code ASC, department ASC, display_name ASC
                """
            ),
            params,
        ).mappings().all()
        profiles = _time_profiles_from_rows(list(rows))
        if profiles:
            return EmployeeTimeProfileCatalogOut(source="database", profiles=profiles, kpis=_profile_kpis(profiles))
    except Exception:
        profiles = []
    else:
        profiles = []

    try:
        user_rows = db.execute(
            text(
                """
                SELECT id, username, email, first_name, last_name, roles, is_active, preferences
                FROM domain_shared.users
                WHERE tenant_id = :tenant_id
                ORDER BY last_name ASC, first_name ASC, username ASC
                """
            ),
            {"tenant_id": tenant_id},
        ).mappings().all()
        profiles = _time_profiles_from_user_rows(list(user_rows))
        if status:
            normalized_status = _normalize_time_profile_status(status)
            profiles = [profile for profile in profiles if profile.status == normalized_status]
        if role:
            profiles = [profile for profile in profiles if profile.roleCode == role]
        if profiles:
            return EmployeeTimeProfileCatalogOut(source="users-fallback", profiles=profiles, kpis=_profile_kpis(profiles))
    except Exception:
        profiles = []

    profiles = _pilot_time_profiles()
    if status:
        normalized_status = _normalize_time_profile_status(status)
        profiles = [profile for profile in profiles if profile.status == normalized_status]
    if role:
        profiles = [profile for profile in profiles if profile.roleCode == role]
    return EmployeeTimeProfileCatalogOut(source="pilot-fallback", profiles=profiles, kpis=_profile_kpis(profiles))


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


@router.post("/time-entries", response_model=TimeEntryBookingOut, status_code=201)
async def create_time_entry(
    payload: TimeEntryBookingCreateIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    entry_id = str(uuid4())
    entry_date = _parse_entry_date(payload.datum)
    row = db.execute(
        text(
            """
            INSERT INTO domain_hr.time_entries
              (id, tenant_id, employee_ref, entry_date, start_time, end_time, hours,
               entry_type, source, status, cost_center, work_area, notes, created_at, updated_at)
            VALUES
              (:id, :tenant_id, :employee_ref, :entry_date, :start_time, :end_time, :hours,
               :entry_type, :source, 'Draft', :cost_center, :work_area, :notes, NOW(), NOW())
            RETURNING id, employee_ref, entry_date, start_time, end_time, hours, entry_type,
                      source, status, cost_center, work_area, correction_reason, approved_by,
                      approved_at, audit_ref
            """
        ),
        {
            "id": entry_id,
            "tenant_id": tenant_id,
            "employee_ref": payload.employeeRef,
            "entry_date": entry_date,
            "start_time": payload.startTime,
            "end_time": payload.endTime,
            "hours": payload.hours,
            "entry_type": payload.entryType,
            "source": payload.source,
            "cost_center": payload.costCenter,
            "work_area": payload.workArea,
            "notes": payload.notes,
        },
    ).mappings().first()
    db.commit()
    return _time_booking_from_row(row)


@router.post("/time-entries/{entry_id}/submit", response_model=TimeEntryActionOut)
async def submit_time_entry(
    entry_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = db.execute(
        text(
            """
            UPDATE domain_hr.time_entries
            SET status = 'Submitted', updated_at = NOW(), version = version + 1
            WHERE id = :entry_id
              AND tenant_id = :tenant_id
              AND status IN ('Draft', 'Rejected', 'Corrected')
            RETURNING id, employee_ref, entry_date, start_time, end_time, hours, entry_type,
                      source, status, cost_center, work_area, correction_reason, approved_by,
                      approved_at, audit_ref
            """
        ),
        {"entry_id": entry_id, "tenant_id": tenant_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=409, detail="Zeitbuchung kann in diesem Status nicht eingereicht werden")
    db.commit()
    return TimeEntryActionOut(ok=True, entry=_time_booking_from_row(row))


@router.post("/time-entries/{entry_id}/approve", response_model=TimeEntryActionOut)
async def approve_time_entry(
    entry_id: str,
    payload: TimeEntryApproveIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = db.execute(
        text(
            """
            UPDATE domain_hr.time_entries
            SET status = 'Approved',
                approved_by = :approved_by,
                approved_at = NOW(),
                updated_at = NOW(),
                version = version + 1
            WHERE id = :entry_id
              AND tenant_id = :tenant_id
              AND status = 'Submitted'
            RETURNING id, employee_ref, entry_date, start_time, end_time, hours, entry_type,
                      source, status, cost_center, work_area, correction_reason, approved_by,
                      approved_at, audit_ref
            """
        ),
        {"entry_id": entry_id, "tenant_id": tenant_id, "approved_by": payload.approvedBy},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=409, detail="Zeitbuchung muss vor Freigabe eingereicht sein")
    db.commit()
    return TimeEntryActionOut(ok=True, entry=_time_booking_from_row(row))


@router.post("/time-entries/{entry_id}/correct", response_model=TimeEntryActionOut)
async def correct_time_entry(
    entry_id: str,
    payload: TimeEntryBookingCorrectionIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    current = db.execute(
        text(
            """
            SELECT status
            FROM domain_hr.time_entries
            WHERE id = :entry_id AND tenant_id = :tenant_id
            """
        ),
        {"entry_id": entry_id, "tenant_id": tenant_id},
    ).mappings().first()
    if not current:
        raise HTTPException(status_code=404, detail="Zeitbuchung nicht gefunden")
    if str(current.get("status")) == "Exported":
        raise HTTPException(status_code=409, detail="Exportierte Zeitbuchungen duerfen nicht still veraendert werden")

    row = db.execute(
        text(
            """
            UPDATE domain_hr.time_entries
            SET start_time = :start_time,
                end_time = :end_time,
                hours = :hours,
                entry_type = :entry_type,
                status = 'Corrected',
                cost_center = :cost_center,
                work_area = :work_area,
                correction_reason = :correction_reason,
                notes = :notes,
                updated_at = NOW(),
                version = version + 1
            WHERE id = :entry_id AND tenant_id = :tenant_id
            RETURNING id, employee_ref, entry_date, start_time, end_time, hours, entry_type,
                      source, status, cost_center, work_area, correction_reason, approved_by,
                      approved_at, audit_ref
            """
        ),
        {
            "entry_id": entry_id,
            "tenant_id": tenant_id,
            "start_time": payload.startTime,
            "end_time": payload.endTime,
            "hours": payload.hours,
            "entry_type": payload.entryType,
            "cost_center": payload.costCenter,
            "work_area": payload.workArea,
            "correction_reason": payload.correctionReason,
            "notes": payload.notes,
        },
    ).mappings().first()
    db.commit()
    return TimeEntryActionOut(ok=True, entry=_time_booking_from_row(row))


@router.get("/absences", response_model=list[AbsenceOut])
async def list_absences(
    datum_von: str | None = Query(default=None),
    datum_bis: str | None = Query(default=None),
    status: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    params: dict[str, Any] = {"tenant_id": tenant_id}
    where = ["tenant_id = :tenant_id", "entry_type IN ('Urlaub', 'Krank', 'Unbezahlt', 'Sonstiges')"]
    if datum_von:
        params["datum_von"] = _parse_entry_date(datum_von)
        where.append("entry_date >= :datum_von")
    if datum_bis:
        params["datum_bis"] = _parse_entry_date(datum_bis)
        where.append("entry_date <= :datum_bis")
    if status:
        params["status"] = status
        where.append("status = :status")

    rows = db.execute(
        text(
            f"""
            SELECT id, employee_ref, entry_date, entry_type, source, status, notes, audit_ref
            FROM domain_hr.time_entries
            WHERE {' AND '.join(where)}
            ORDER BY entry_date ASC, employee_ref ASC
            """
        ),
        params,
    ).mappings().all()
    return [_absence_from_row(row) for row in rows]


@router.post("/absences/import", response_model=AbsenceImportOut, status_code=201)
async def import_absence(
    payload: AbsenceImportIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    from_date = _parse_entry_date(payload.fromDate)
    to_date = _parse_entry_date(payload.toDate)
    imported: list[AbsenceOut] = []
    for entry_date in _date_range(from_date, to_date):
        row = db.execute(
            text(
                """
                INSERT INTO domain_hr.time_entries
                  (id, tenant_id, employee_ref, entry_date, start_time, end_time, hours,
                   entry_type, source, status, notes, audit_ref, created_at, updated_at)
                VALUES
                  (:id, :tenant_id, :employee_ref, :entry_date, NULL, NULL, 0,
                   :entry_type, 'absence', :status, :notes, :audit_ref, NOW(), NOW())
                RETURNING id, employee_ref, entry_date, entry_type, source, status, notes, audit_ref
                """
            ),
            {
                "id": str(uuid4()),
                "tenant_id": tenant_id,
                "employee_ref": payload.employeeRef,
                "entry_date": entry_date,
                "entry_type": payload.absenceType,
                "status": payload.status,
                "notes": payload.note or payload.sourceSystem,
                "audit_ref": payload.externalRef or f"{payload.sourceSystem}:{payload.employeeRef}:{entry_date.isoformat()}",
            },
        ).mappings().first()
        imported.append(_absence_from_row(row))
    db.commit()
    return AbsenceImportOut(ok=True, imported=len(imported), absences=imported)


@router.get("/shifts", response_model=list[ShiftOut])
async def list_shifts(
    datum_von: str | None = Query(default=None),
    datum_bis: str | None = Query(default=None),
    location: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    params: dict[str, Any] = {"tenant_id": tenant_id}
    where = ["tenant_id = :tenant_id"]
    if datum_von:
        params["datum_von"] = _parse_entry_date(datum_von)
        where.append("shift_date >= :datum_von")
    if datum_bis:
        params["datum_bis"] = _parse_entry_date(datum_bis)
        where.append("shift_date <= :datum_bis")
    if location:
        params["location"] = location
        where.append("location_code = :location")

    rows = db.execute(
        text(
            f"""
            SELECT id, shift_date, name, location_code, required_role, required_qualifications,
                   required_headcount, starts_at, ends_at, assigned_employee_refs, status,
                   conflicts, notes
            FROM domain_hr.shifts
            WHERE {' AND '.join(where)}
            ORDER BY shift_date ASC, starts_at ASC, location_code ASC
            """
        ),
        params,
    ).mappings().all()
    return [_shift_from_row(row) for row in rows]


@router.post("/shifts", response_model=ShiftOut, status_code=201)
async def create_shift(
    payload: ShiftCreateIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    shift_date = _parse_entry_date(payload.datum)
    profile_rows = db.execute(
        text(
            """
            SELECT employee_ref, status, qualifications
            FROM domain_hr.employee_time_profiles
            WHERE tenant_id = :tenant_id
            """
        ),
        {"tenant_id": tenant_id},
    ).mappings().all()
    absence_rows = db.execute(
        text(
            """
            SELECT employee_ref
            FROM domain_hr.time_entries
            WHERE tenant_id = :tenant_id
              AND entry_date = :shift_date
              AND entry_type IN ('Urlaub', 'Krank', 'Unbezahlt', 'Sonstiges')
              AND status IN ('Approved', 'Genehmigt')
            """
        ),
        {"tenant_id": tenant_id, "shift_date": shift_date},
    ).mappings().all()
    conflicts = _build_shift_conflicts(
        assigned_employee_refs=payload.assignedEmployeeRefs,
        required_headcount=payload.requiredHeadcount,
        required_qualifications=payload.requiredQualifications,
        profile_rows=list(profile_rows),
        absence_rows=list(absence_rows),
    )
    status = _shift_status(conflicts)
    row = db.execute(
        text(
            """
            INSERT INTO domain_hr.shifts
              (id, tenant_id, shift_date, name, location_code, required_role,
               required_qualifications, required_headcount, starts_at, ends_at,
               assigned_employee_refs, status, conflicts, notes, created_at, updated_at)
            VALUES
              (:id, :tenant_id, :shift_date, :name, :location_code, :required_role,
               CAST(:required_qualifications AS jsonb), :required_headcount, :starts_at, :ends_at,
               CAST(:assigned_employee_refs AS jsonb), :status, CAST(:conflicts AS jsonb),
               :notes, NOW(), NOW())
            RETURNING id, shift_date, name, location_code, required_role, required_qualifications,
                      required_headcount, starts_at, ends_at, assigned_employee_refs, status,
                      conflicts, notes
            """
        ),
        {
            "id": str(uuid4()),
            "tenant_id": tenant_id,
            "shift_date": shift_date,
            "name": payload.name,
            "location_code": payload.locationCode,
            "required_role": payload.requiredRole,
            "required_qualifications": json.dumps(payload.requiredQualifications),
            "required_headcount": payload.requiredHeadcount,
            "starts_at": payload.startTime,
            "ends_at": payload.endTime,
            "assigned_employee_refs": json.dumps(payload.assignedEmployeeRefs),
            "status": status,
            "conflicts": json.dumps([conflict.model_dump() for conflict in conflicts]),
            "notes": payload.notes,
        },
    ).mappings().first()
    db.commit()
    return _shift_from_row(row)


@router.get("/driver-time/summary", response_model=DriverTimeSummaryOut)
async def get_driver_time_summary(
    datum: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    target_date = datum or datetime.utcnow().date().isoformat()
    params: dict[str, Any] = {"tenant_id": tenant_id, "entry_date": target_date}

    try:
        timesheet_rows = db.execute(
            text(
                """
                SELECT id, entry_date, driver_name, vehicle_plate, tours, total_hours, overtime_hours, created_at
                FROM domain_hr.driver_timesheets
                WHERE tenant_id = :tenant_id AND entry_date = :entry_date
                ORDER BY driver_name ASC, created_at ASC
                """
            ),
            params,
        ).mappings().all()
        absence_rows = db.execute(
            text(
                """
                SELECT employee_ref, entry_date, entry_type
                FROM domain_hr.time_entries
                WHERE tenant_id = :tenant_id
                  AND entry_date = :entry_date
                  AND entry_type IN ('Urlaub', 'Krank')
                """
            ),
            params,
        ).mappings().all()
    except Exception:
        pilot_events = _driver_time_pilot_events(target_date)
        return _build_driver_time_summary(target_date, pilot_events, source="pilot-fallback")

    events = _events_from_timesheets(list(timesheet_rows))
    if not events:
        pilot_events = _driver_time_pilot_events(target_date)
        return _build_driver_time_summary(target_date, pilot_events, source="pilot-empty")

    return _build_driver_time_summary(
        target_date,
        events,
        absence_ranges=_approved_absence_ranges(list(absence_rows)),
        source="database",
    )


@router.get("/time-cockpit", response_model=TimeCockpitOut)
async def get_time_cockpit(
    datum: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    target_date = datum or datetime.utcnow().date().isoformat()
    params: dict[str, Any] = {"tenant_id": tenant_id, "entry_date": target_date}

    driver_time = await get_driver_time_summary(datum=target_date, tenant_id=tenant_id, db=db)
    try:
        rows = db.execute(
            text(
                """
                SELECT id, employee_ref, entry_date, start_time, end_time, hours, entry_type, source, status
                FROM domain_hr.time_entries
                WHERE tenant_id = :tenant_id AND entry_date = :entry_date
                ORDER BY employee_ref ASC, start_time ASC
                """
            ),
            params,
        ).mappings().all()
    except Exception:
        entries = _pilot_time_entries(target_date)
        return _build_time_cockpit(target_date, entries, driver_time, source="pilot-fallback")

    entries = _time_rows_to_entries(list(rows))
    if not entries:
        entries = _pilot_time_entries(target_date)
        return _build_time_cockpit(target_date, entries, driver_time, source="pilot-empty")

    return _build_time_cockpit(target_date, entries, driver_time, source="database")


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
