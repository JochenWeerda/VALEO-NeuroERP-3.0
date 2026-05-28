"""Pydantic schemas for the HR/Personal domain.

Shared between app/api/v1/endpoints/personal.py (route handlers)
and app/services/personal_service.py (business logic that builds responses).
Import these instead of defining locally.
"""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


# ── HRM Readiness ─────────────────────────────────────────────────────────────

class HrmReadinessCapabilityOut(BaseModel):
    id: str
    title: str
    status: str
    priority: str
    legalBasis: list[str] = Field(default_factory=list)
    implementedEvidence: list[str] = Field(default_factory=list)
    missingCapabilities: list[str] = Field(default_factory=list)
    nextSlices: list[str] = Field(default_factory=list)
    controls: list[str] = Field(default_factory=list)


class HrmReadinessIntegrationOut(BaseModel):
    id: str
    title: str
    status: str
    direction: str
    minimumContract: list[str] = Field(default_factory=list)
    nextSlice: str


class HrmReadinessAiControlOut(BaseModel):
    id: str
    title: str
    classification: str
    allowedUse: list[str] = Field(default_factory=list)
    prohibitedUse: list[str] = Field(default_factory=list)
    requiredControls: list[str] = Field(default_factory=list)


class HrmReadinessOut(BaseModel):
    status: str
    country: str
    asOf: str
    minimumChecklist: list[str]
    capabilities: list[HrmReadinessCapabilityOut]
    integrations: list[HrmReadinessIntegrationOut]
    aiControls: list[HrmReadinessAiControlOut]
    residualRisks: list[str]


# ── HRM Operating System ──────────────────────────────────────────────────────

class HrmOperatingSystemModuleOut(BaseModel):
    id: str
    title: str
    status: str
    apiContracts: list[str]
    controls: list[str]
    externalGates: list[str] = Field(default_factory=list)


class HrmOperatingSystemOut(BaseModel):
    status: str
    asOf: str
    closedRepoGaps: list[str]
    modules: list[HrmOperatingSystemModuleOut]
    timeEntryModelRules: list[str]
    externalOperatingGates: list[str]


# ── HRM Operations Gates ──────────────────────────────────────────────────────

class HrmOperationsGateOut(BaseModel):
    id: str
    title: str
    status: str
    ownerRole: str
    goLiveBlocking: bool
    priority: str = "P1"
    riskLevel: str = "mittel"
    dueDate: str | None = None
    lastChangedAt: str | None = None
    allowedRoles: list[str] = Field(default_factory=list)
    readOnlyRoles: list[str] = Field(default_factory=list)
    evidenceCount: int = 0
    latestEvidenceRef: str | None = None
    lastProbeStatus: str | None = None
    lastProbeAt: str | None = None
    approvedBy: str | None = None
    approvedAt: str | None = None
    rejectionReason: str | None = None
    evidenceRequired: list[str]
    acceptanceCriteria: list[str]
    auditTrail: list[str]
    professionalPractice: list[str]


class HrmOperationsGatesOut(BaseModel):
    status: str
    asOf: str
    goLiveAllowed: bool
    summary: str
    gates: list[HrmOperationsGateOut]
    closureDefinition: list[str]


class HrmOperationsGateEvidenceIn(BaseModel):
    evidenceType: str = Field(..., min_length=2, max_length=80)
    title: str = Field(..., min_length=2, max_length=220)
    artifactRef: str = Field(..., min_length=2, max_length=500)
    submittedBy: str = Field(..., min_length=2, max_length=160)
    metadata: dict[str, Any] = Field(default_factory=dict)


class HrmOperationsGateEvidenceOut(BaseModel):
    id: str
    gateId: str
    evidenceType: str
    title: str
    artifactRef: str
    submittedBy: str
    submittedAt: str
    metadata: dict[str, Any]


class HrmOperationsGateDecisionIn(BaseModel):
    decision: str = Field(..., pattern="^(approve|reject)$")
    decidedBy: str = Field(..., min_length=2, max_length=160)
    reason: str | None = Field(default=None, max_length=1000)


class HrmOperationsGateProbeIn(BaseModel):
    provider: str = Field(..., min_length=2, max_length=120)
    probeType: str = Field(..., min_length=2, max_length=80)
    result: str = Field(..., pattern="^(passed|failed|manual|not_configured)$")
    performedBy: str = Field(..., min_length=2, max_length=160)
    details: dict[str, Any] = Field(default_factory=dict)


class HrmOperationsGateProbeOut(BaseModel):
    id: str
    gateId: str
    provider: str
    probeType: str
    result: str
    performedBy: str
    performedAt: str
    details: dict[str, Any]


class HrmOperationsGateActionOut(BaseModel):
    ok: bool
    gate: HrmOperationsGateOut


class HrmOperationsGoLivePolicyOut(BaseModel):
    goLiveAllowed: bool
    blockerCount: int
    blockers: list[HrmOperationsGateOut]
    status: str
    summary: str


# ── Employee File ─────────────────────────────────────────────────────────────

class EmployeeFileDocumentClassOut(BaseModel):
    documentType: str
    title: str
    legalBasis: list[str]
    defaultVisibility: str
    retentionYears: int
    requiresDmsRef: bool
    deletionRule: str


class EmployeeFileDocumentCreateIn(BaseModel):
    documentType: str = Field(..., min_length=1, max_length=80)
    title: str = Field(..., min_length=1, max_length=180)
    issuedAt: str | None = None
    validUntil: str | None = None
    dmsDocumentId: str | None = Field(default=None, max_length=160)
    visibility: str | None = Field(default=None, pattern="^(employee|manager|hr|payroll)$")
    notes: str | None = Field(default=None, max_length=500)
    createdBy: str = Field(default="system", max_length=120)


class EmployeeFileDocumentOut(BaseModel):
    id: str
    employeeRef: str
    documentType: str
    title: str
    status: str
    visibility: str
    legalBasis: list[str]
    issuedAt: str | None = None
    validUntil: str | None = None
    retentionUntil: str
    dmsDocumentId: str | None = None
    canEmployeeView: bool
    canManagerView: bool
    deletionBlockedReason: str
    auditRef: str


class EmployeeFileExportOut(BaseModel):
    available: bool
    format: str
    includesAuditTrail: bool
    includesRetentionPlan: bool
    dataSubjectAccessHint: str


class EmployeeFileRetentionOut(BaseModel):
    deletionConcept: str
    reviewCadence: str
    blockedDocumentCount: int
    nextReviewHint: str


class EmployeeFileOut(BaseModel):
    employeeRef: str
    source: str
    actorRole: str
    documentClasses: list[EmployeeFileDocumentClassOut]
    documents: list[EmployeeFileDocumentOut]
    hiddenDocumentCount: int
    exportPackage: EmployeeFileExportOut
    retention: EmployeeFileRetentionOut


# --- Extracted from endpoint file ---
class PersonalOut(BaseSchema):
    """Typed response schema for PersonalOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


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


class CalendarEventIn(BaseModel):
    sourceSystem: str = Field(default="valeo", max_length=80)
    provider: str = Field(default="internal", max_length=40)
    externalEventRef: str | None = Field(default=None, max_length=160)
    eventType: str = Field(..., min_length=1, max_length=60)
    title: str = Field(..., min_length=1, max_length=200)
    employeeRef: str | None = Field(default=None, max_length=120)
    resourceRef: str | None = Field(default=None, max_length=120)
    startsAt: str
    endsAt: str
    timezone: str = Field(default="Europe/Berlin", max_length=80)
    visibility: str = Field(default="team", pattern="^(public|team|private|busy_only)$")
    status: str = Field(default="confirmed", max_length=40)
    syncState: str = Field(default="local", pattern="^(local|pending|synced|failed)$")
    conflictLevel: str = Field(default="none", pattern="^(none|warning|blocker)$")
    sourceRef: str | None = Field(default=None, max_length=160)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CalendarEventOut(BaseModel):
    id: str
    sourceSystem: str
    provider: str
    externalEventRef: str | None = None
    eventType: str
    title: str
    employeeRef: str | None = None
    resourceRef: str | None = None
    startsAt: str
    endsAt: str
    timezone: str
    visibility: str
    status: str
    syncState: str
    conflictLevel: str
    sourceRef: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class PayrollExportCreateIn(BaseModel):
    periodFrom: str
    periodTo: str
    targetSystem: str = Field(default="datev", max_length=40)
    createdBy: str | None = Field(default=None, max_length=120)


class PayrollExportItemOut(BaseModel):
    employeeRef: str
    datum: str
    hours: float
    entryType: str
    wageType: str
    costCenter: str | None = None
    sourceEntryId: str


class PayrollExportBlockerOut(BaseModel):
    code: str
    message: str
    employeeRef: str | None = None
    sourceEntryId: str | None = None


class PayrollExportOut(BaseModel):
    id: str
    periodFrom: str
    periodTo: str
    targetSystem: str
    status: str
    items: list[PayrollExportItemOut] = Field(default_factory=list)
    blockers: list[PayrollExportBlockerOut] = Field(default_factory=list)


class CampaignCapacityFindingOut(BaseModel):
    code: str
    severity: str
    message: str
    roleCode: str | None = None


class CampaignCapacityCreateIn(BaseModel):
    campaignCode: str = Field(..., min_length=1, max_length=80)
    name: str = Field(..., min_length=1, max_length=200)
    periodFrom: str
    periodTo: str
    locationCode: str = Field(default="main", max_length=80)
    roleDemand: dict[str, int] = Field(default_factory=dict)
    expectedVolume: float | None = None


class CampaignCapacityOut(BaseModel):
    id: str
    campaignCode: str
    name: str
    periodFrom: str
    periodTo: str
    locationCode: str
    roleDemand: dict[str, int]
    expectedVolume: float | None = None
    status: str
    findings: list[CampaignCapacityFindingOut] = Field(default_factory=list)


class FieldServiceConflictOut(BaseModel):
    code: str
    severity: str
    message: str


class FieldServicePlanCreateIn(BaseModel):
    employeeRef: str = Field(..., min_length=1, max_length=120)
    customerRef: str = Field(..., min_length=1, max_length=120)
    territoryCode: str = Field(..., min_length=1, max_length=80)
    campaignCode: str | None = Field(default=None, max_length=80)
    visitType: str = Field(default="consulting", max_length=60)
    startsAt: str
    endsAt: str
    notes: str | None = Field(default=None, max_length=500)


class FieldServicePlanOut(BaseModel):
    id: str
    employeeRef: str
    customerRef: str
    territoryCode: str
    campaignCode: str | None = None
    visitType: str
    startsAt: str
    endsAt: str
    status: str
    conflicts: list[FieldServiceConflictOut] = Field(default_factory=list)
    notes: str | None = None


class PlanningPreferenceOut(BaseModel):
    employeeRef: str
    prefersNightTours: bool = False
    avoidNightTours: bool = False
    childcareSensitive: bool = False
    preferredWeekdays: list[str] = Field(default_factory=list)
    schoolHolidayRegions: list[str] = Field(default_factory=list)
    bridgeDayPolicy: str = "normal"
    maxExtraHoursBeforeHoliday: float = 2.0


class WorkPlanFindingOut(BaseModel):
    code: str
    severity: str
    message: str
    employeeRef: str | None = None
    datum: str | None = None
    sourceRef: str | None = None


class WorkPlanAssignmentOut(BaseModel):
    id: str
    datum: str
    employeeRef: str
    label: str
    sourceType: str
    startTime: str | None = None
    endTime: str | None = None
    status: str
    printReady: bool
    findings: list[WorkPlanFindingOut] = Field(default_factory=list)


class WorkPlanOut(BaseModel):
    periodFrom: str
    periodTo: str
    source: str
    preferences: list[PlanningPreferenceOut] = Field(default_factory=list)
    assignments: list[WorkPlanAssignmentOut] = Field(default_factory=list)
    findings: list[WorkPlanFindingOut] = Field(default_factory=list)
    printTitle: str
    generatedAt: str


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


class DriverTimeEventIn(BaseModel):
    employee_ref: str
    vehicle_id: str | None = None
    tour_ref: str | None = None
    event_type: Literal["START", "END", "BREAK", "PAUSE", "TACHO"]
    event_ts: str  # ISO datetime
    duration_minutes: int | None = None
    absence_ref: str | None = None
    source: Literal["MANUAL", "TACHO", "IMPORT", "SYSTEM"] = "MANUAL"
    notes: str | None = None


class DriverTimeCollisionOut(BaseModel):
    event_id: str
    employee_ref: str
    event_ts: str
    absence_ref: str
    collision_type: str


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


class OrgUnitIn(BaseModel):
    unit_code: str = Field(..., max_length=40)
    name: str = Field(..., max_length=200)
    unit_type: str = Field(default="ABTEILUNG", pattern="^(ABTEILUNG|TEAM|STANDORT|KOSTENSTELLE)$")
    parent_id: str | None = None
    cost_center_id: str | None = None
    manager_ref: str | None = None


class TimeAccountAdjustIn(BaseModel):
    delta_hours: float = Field(..., description="Positive = Gutschrift, Negative = Abbuchung")
    reason: str = Field(..., max_length=400)
    adjustment_date: str | None = None  # ISO date, default: today


class ApplicationIn(BaseModel):
    applicant_name: str = Field(..., max_length=200)
    applicant_email: str = Field(..., max_length=200)
    position_id: str | None = None
    position_title: str | None = Field(default=None, max_length=200)
    source: str | None = Field(default=None, max_length=80)
    documents_ref: str | None = None


class LohnBerechnungRequest(BaseModel):
    brutto: float = Field(..., gt=0, description="Monatliches Bruttogehalt EUR")
    steuerklasse: int = Field(..., ge=1, le=6)
    hat_kinder: bool = False
    kinder_freibetraege: float = Field(0.0, ge=0)
    kirchensteuersatz: float = Field(0.09, ge=0, le=0.12, description="0,08 (BaWü/Bay) oder 0,09")
    zusatzbeitrag_kv: float = Field(0.017, ge=0, le=0.04, description="Individueller KV-Zusatzbeitrag (ø 2025: 1,7 %)")

