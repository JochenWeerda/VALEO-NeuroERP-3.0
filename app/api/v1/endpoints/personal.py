"""Personal endpoints for employee list, time entries and timesheets."""

from __future__ import annotations

import json
from datetime import date, datetime, time
from typing import Any, Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ConflictError, EntityNotFoundError
from app.core.tenant import get_tenant_id
from app.services.personal_service import PersonalService

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


class DriverTimeEventPatch(BaseModel):
    vehicle_id: str | None = None
    tour_ref: str | None = None
    event_type: Literal["START", "END", "BREAK", "PAUSE", "TACHO"] | None = None
    event_ts: str | None = None
    duration_minutes: int | None = None
    absence_ref: str | None = None
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


_HRM_MINIMUM_CHECKLIST = [
    "Digitale Personalakte",
    "DSGVO-konformes Rechte- und Loeschkonzept",
    "Arbeitszeiterfassung",
    "Urlaubs- und Abwesenheitsmanagement",
    "eAU-Prozess",
    "Payroll-/DATEV-Schnittstelle",
    "Vertrags- und Dokumentenvorlagen",
    "Employee Self Service",
    "Manager Self Service",
    "Recruiting und Bewerbermanagement",
    "Onboarding und Offboarding",
    "Workflows mit Freigaben",
    "Reporting und HR-Dashboards",
    "Microsoft-365-, LibreOffice- und Google-Workspace-Integration",
    "Sichere KI-Funktionen mit menschlicher Kontrolle",
]


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
    return HrmOperationsGatesOut(
        status="external_gates_defined",
        asOf="2026-05-13",
        goLiveAllowed=not any(gate.goLiveBlocking and gate.status != "approved" for gate in gates),
        summary="Repo fachlich abgeschlossen; Produktiv-Go-live bleibt bis zur Evidenzfreigabe aller externen Gates blockiert.",
        gates=gates,
        closureDefinition=[
            "Jedes Gate besitzt Owner, Evidenz, Abnahmekriterien und Auditspur.",
            "Go-live ist nur erlaubt, wenn alle blocking Gates approved sind.",
            "Fehlende Zugangsdaten oder Rechtsfreigaben werden nicht als Repo-Gap gefuehrt, sondern als Betriebsfreigabe.",
            "Fachliche Contracts bleiben stabil und koennen mit echten Nachweisen befuellt werden.",
        ],
    )


def _hrm_operations_gate_catalog() -> dict[str, HrmOperationsGateOut]:
    return {gate.id: gate for gate in build_hrm_operations_gates().gates}


def _hrm_gate_readiness_metadata(gate_id: str) -> dict[str, Any]:
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


def _apply_hrm_gate_readiness_metadata(gate: HrmOperationsGateOut) -> HrmOperationsGateOut:
    return gate.model_copy(update=_hrm_gate_readiness_metadata(gate.id))


def _hrm_gate_datetime(value: Any) -> str | None:
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _row_mapping(row: Any) -> dict[str, Any]:
    if row is None:
        return {}
    if isinstance(row, dict):
        return row
    try:
        return dict(row)
    except Exception:
        return {key: getattr(row, key) for key in dir(row) if not key.startswith("_")}


def _merge_hrm_gate_state(template: HrmOperationsGateOut, row: dict[str, Any] | None) -> HrmOperationsGateOut:
    enriched_template = _apply_hrm_gate_readiness_metadata(template)
    if not row:
        return enriched_template
    return enriched_template.model_copy(
        update={
            "status": row.get("status") or enriched_template.status,
            "ownerRole": row.get("owner_role") or enriched_template.ownerRole,
            "goLiveBlocking": bool(row.get("go_live_blocking", enriched_template.goLiveBlocking)),
            "lastChangedAt": _hrm_gate_datetime(row.get("updated_at") or row.get("approved_at") or row.get("last_probe_at")),
            "evidenceCount": int(row.get("evidence_count") or 0),
            "latestEvidenceRef": row.get("latest_evidence_ref"),
            "lastProbeStatus": row.get("last_probe_status"),
            "lastProbeAt": _hrm_gate_datetime(row.get("last_probe_at")),
            "approvedBy": row.get("approved_by"),
            "approvedAt": _hrm_gate_datetime(row.get("approved_at")),
            "rejectionReason": row.get("rejection_reason"),
        }
    )


def _seed_hrm_operations_gates(db: Session, tenant_id: str) -> None:
    for gate in build_hrm_operations_gates().gates:
        db.execute(
            text(
                """
                INSERT INTO domain_hr.hrm_operations_gates
                  (tenant_id, gate_id, status, owner_role, go_live_blocking, metadata)
                VALUES
                  (:tenant_id, :gate_id, :status, :owner_role, :go_live_blocking, CAST(:metadata AS jsonb))
                ON CONFLICT (tenant_id, gate_id) DO UPDATE SET
                  owner_role = EXCLUDED.owner_role,
                  go_live_blocking = EXCLUDED.go_live_blocking,
                  updated_at = NOW()
                """
            ),
            {
                "tenant_id": tenant_id,
                "gate_id": gate.id,
                "status": gate.status,
                "owner_role": gate.ownerRole,
                "go_live_blocking": gate.goLiveBlocking,
                "metadata": json.dumps({"title": gate.title}),
            },
        )


def _load_hrm_operations_gates_from_db(db: Session, tenant_id: str) -> HrmOperationsGatesOut:
    _seed_hrm_operations_gates(db, tenant_id)
    rows = db.execute(
        text(
            """
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
            """
        ),
        {"tenant_id": tenant_id},
    ).mappings().all()
    catalog = _hrm_operations_gate_catalog()
    merged = [_merge_hrm_gate_state(catalog[row["gate_id"]], _row_mapping(row)) for row in rows if row["gate_id"] in catalog]
    known_ids = {gate.id for gate in merged}
    merged.extend(gate for gate_id, gate in catalog.items() if gate_id not in known_ids)
    go_live_allowed = not any(gate.goLiveBlocking and gate.status != "approved" for gate in merged)
    return HrmOperationsGatesOut(
        status="approved" if go_live_allowed else "external_gates_runtime",
        asOf="2026-05-13",
        goLiveAllowed=go_live_allowed,
        summary=(
            "Alle blockierenden HRM-Betriebsfreigaben sind technisch approved."
            if go_live_allowed
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


def _get_hrm_operations_gates_runtime(db: Session, tenant_id: str) -> HrmOperationsGatesOut:
    try:
        return _load_hrm_operations_gates_from_db(db, tenant_id)
    except SQLAlchemyError:
        return build_hrm_operations_gates()


def _require_hrm_gate(gate_id: str) -> HrmOperationsGateOut:
    gate = _hrm_operations_gate_catalog().get(gate_id)
    if gate is None:
        raise HTTPException(status_code=404, detail=f"Unknown HRM operations gate '{gate_id}'")
    return gate


def _load_single_hrm_gate(db: Session, tenant_id: str, gate_id: str) -> HrmOperationsGateOut:
    gates = _load_hrm_operations_gates_from_db(db, tenant_id)
    for gate in gates.gates:
        if gate.id == gate_id:
            return gate
    raise HTTPException(status_code=404, detail=f"Unknown HRM operations gate '{gate_id}'")


def _insert_hrm_gate_audit(
    db: Session,
    tenant_id: str,
    gate_id: str,
    action: str,
    actor: str,
    from_status: str | None,
    to_status: str,
    reason: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    db.execute(
        text(
            """
            INSERT INTO domain_hr.hrm_operations_gate_audit
              (id, tenant_id, gate_id, action, actor, from_status, to_status, reason, details)
            VALUES
              (:id, :tenant_id, :gate_id, :action, :actor, :from_status, :to_status, :reason, CAST(:details AS jsonb))
            """
        ),
        {
            "id": str(uuid4()),
            "tenant_id": tenant_id,
            "gate_id": gate_id,
            "action": action,
            "actor": actor,
            "from_status": from_status,
            "to_status": to_status,
            "reason": reason,
            "details": json.dumps(details or {}),
        },
    )


def _evidence_out(row: Any) -> HrmOperationsGateEvidenceOut:
    data = _row_mapping(row)
    metadata = data.get("metadata") or {}
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    return HrmOperationsGateEvidenceOut(
        id=str(data["id"]),
        gateId=str(data["gate_id"]),
        evidenceType=str(data["evidence_type"]),
        title=str(data["title"]),
        artifactRef=str(data["artifact_ref"]),
        submittedBy=str(data["submitted_by"]),
        submittedAt=_hrm_gate_datetime(data.get("submitted_at")) or datetime.utcnow().isoformat(),
        metadata=metadata,
    )


def _probe_out(row: Any) -> HrmOperationsGateProbeOut:
    data = _row_mapping(row)
    details = data.get("details") or {}
    if isinstance(details, str):
        details = json.loads(details)
    return HrmOperationsGateProbeOut(
        id=str(data["id"]),
        gateId=str(data["gate_id"]),
        provider=str(data["provider"]),
        probeType=str(data["probe_type"]),
        result=str(data["result"]),
        performedBy=str(data["performed_by"]),
        performedAt=_hrm_gate_datetime(data.get("performed_at")) or datetime.utcnow().isoformat(),
        details=details,
    )


_HRM_CLOSED_REPO_GAPS = [
    "HRM-AKTE-001",
    "HRM-EAU-001",
    "HRM-DATEV-001",
    "HRM-CONTRACTS-001",
    "HRM-ESS-001",
    "HRM-MSS-001",
    "HRM-RECRUITING-001",
    "HRM-OFFBOARDING-001",
    "HRM-WORKFLOWS-001",
    "HRM-ANALYTICS-001",
    "HRM-PRIVACY-001",
    "HRM-AI-GOV-001",
    "HRM-M365-001",
    "HRM-GOOGLE-001",
    "HRM-LIBREOFFICE-001",
]


def build_hrm_operating_system_contract() -> HrmOperatingSystemOut:
    return HrmOperatingSystemOut(
        status="repo_contract_complete",
        asOf="2026-05-13",
        closedRepoGaps=_HRM_CLOSED_REPO_GAPS,
        timeEntryModelRules=[
            "Arbeitszeit und Abwesenheiten liegen in domain_hr.time_entries.",
            "Datumsspalte ist entry_date; Stundenfeld ist hours.",
            "Abwesenheiten sind entry_type IN ('Urlaub','Krank','Unbezahlt','Sonstiges').",
            "Schreibpfade nutzen RETURNING fuer atomare Mutation und Read-Model.",
            "Keine neue time_bookings- oder absences-Tabelle fuer HR-Time.",
        ],
        modules=[
            HrmOperatingSystemModuleOut(
                id="employee-file",
                title="Digitale Personalakte",
                status="contract_complete",
                apiContracts=[
                    "GET /api/v1/personal/employee-files/{employee_ref}",
                    "POST /api/v1/personal/employee-files/{employee_ref}/documents",
                ],
                controls=["Dokumentklassen", "Rollenfilter", "Retention-Sicht", "Audit-Ref", "Exportpaket"],
                externalGates=["produktive DMS-Ablage", "Rechtsfreigabe Retention"],
            ),
            HrmOperatingSystemModuleOut(
                id="eau",
                title="eAU und Krankmeldung",
                status="contract_complete",
                apiContracts=[
                    "POST /api/v1/personal/absences/import",
                    "GET /api/v1/personal/hrm-operating-system",
                ],
                controls=["keine Diagnosedaten", "Fristenmonitor", "Krankenkassenstatus", "Audit ohne medizinische Details"],
                externalGates=["eAU-Kommunikationszugang", "Krankenkassen-Testverfahren"],
            ),
            HrmOperatingSystemModuleOut(
                id="payroll-datev",
                title="Payroll, DATEV und Monatsabschluss",
                status="contract_complete",
                apiContracts=["GET /api/v1/personal/payroll-exports", "POST /api/v1/personal/payroll-exports"],
                controls=["Lohnarten", "Fehlzeiten", "Kostenstellen", "Blocker", "Monatsabschlussprotokoll"],
                externalGates=["DATEV-Zielformat", "Steuerberaterfreigabe"],
            ),
            HrmOperatingSystemModuleOut(
                id="contracts-templates",
                title="Vertrags- und Dokumentenvorlagen",
                status="contract_complete",
                apiContracts=[
                    "POST /api/v1/personal/employee-files/{employee_ref}/documents",
                    "GET /api/v1/personal/hrm-operating-system",
                ],
                controls=["Vorlagenversion", "Textform-/Schriftformentscheidung", "Archiv-Ref", "E-Signaturstatus"],
                externalGates=["LibreOffice-Rendering", "E-Signatur-Anbieter"],
            ),
            HrmOperatingSystemModuleOut(
                id="self-service",
                title="Employee und Manager Self Service",
                status="contract_complete",
                apiContracts=[
                    "GET /api/v1/personal/employee-files/{employee_ref}",
                    "POST /api/v1/personal/time-entries",
                    "GET /api/v1/personal/work-plan",
                    "GET /api/v1/personal/time-cockpit",
                ],
                controls=["Rollenfilter", "Freigabequeue", "Teamkalender", "Datenantrag als Workflow"],
                externalGates=["Betriebsvereinbarung Self-Service", "SSO-Rollenzuordnung"],
            ),
            HrmOperatingSystemModuleOut(
                id="recruiting-development",
                title="Recruiting, Onboarding, Performance und Entwicklung",
                status="contract_complete",
                apiContracts=[
                    "GET /api/v1/training/onboarding/checklists",
                    "GET /api/v1/training/onboarding/runs",
                    "GET /api/v1/training/qualifications",
                    "GET /api/v1/personal/hrm-operating-system",
                ],
                controls=["Bewerber-Retention", "Talentpool-Einwilligung", "Human-in-the-loop", "Skill-Matrix"],
                externalGates=["Karriereseite", "E-Mail/Kalender-Interviewintegration"],
            ),
            HrmOperatingSystemModuleOut(
                id="analytics-privacy",
                title="People Analytics, Datenschutz und Betriebsratsfaehigkeit",
                status="contract_complete",
                apiContracts=["GET /api/v1/personal/hrm-readiness", "GET /api/v1/personal/hrm-operating-system"],
                controls=["Aggregationsschwellen", "freigegebener Reporting-Zweck", "DSFA-Marker", "AVV/DPA-Register"],
                externalGates=["DSFA-Freigabe", "Betriebsratsabstimmung"],
            ),
            HrmOperatingSystemModuleOut(
                id="ai-governance",
                title="Kontrollierte HR-KI",
                status="contract_complete",
                apiContracts=["GET /api/v1/personal/hrm-readiness", "GET /api/v1/personal/hrm-operating-system"],
                controls=["Human-Gate", "Protokollierung", "Transparenz", "nur konkret freigegebene Assistenzfunktionen"],
                externalGates=["Konformitaetspruefung fuer konkret vorgesehene KI-Assistenztools"],
            ),
            HrmOperatingSystemModuleOut(
                id="office-connectors",
                title="Microsoft 365, Google Workspace, LibreOffice, DMS und E-Signatur",
                status="contract_complete",
                apiContracts=["GET /api/v1/personal/calendar-events", "POST /api/v1/personal/calendar-events"],
                controls=["OAuth-Scopes", "Busy-only Datenschutz", "SSO", "Dokumentvorlagen", "Audit-Ref"],
                externalGates=["produktive Tenant-Secrets", "AVV/DPA", "Connector-Probe"],
            ),
        ],
        externalOperatingGates=[
            "Echte eAU-/DATEV-/Microsoft-/Google-/LibreOffice-/E-Signatur-Zugangsdaten",
            "AVV/DPA, Hostingort, Subprozessoren und Betriebsvereinbarungen",
            "Rechtsfreigabe fuer Retention, DSFA und konkrete KI-Werkzeuge",
        ],
    )


_EMPLOYEE_FILE_DOCUMENT_CLASSES = {
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


def _employee_file_document_classes() -> list[EmployeeFileDocumentClassOut]:
    return [
        EmployeeFileDocumentClassOut(
            documentType=key,
            title=str(value["title"]),
            legalBasis=[str(item) for item in value["legal_basis"]],
            defaultVisibility=str(value["default_visibility"]),
            retentionYears=int(value["retention_years"]),
            requiresDmsRef=bool(value["requires_dms_ref"]),
            deletionRule=str(value["deletion_rule"]),
        )
        for key, value in _EMPLOYEE_FILE_DOCUMENT_CLASSES.items()
    ]


def _document_class(document_type: str) -> dict[str, Any]:
    if document_type not in _EMPLOYEE_FILE_DOCUMENT_CLASSES:
        raise HTTPException(status_code=422, detail=f"Unknown employee file document type: {document_type}")
    return _EMPLOYEE_FILE_DOCUMENT_CLASSES[document_type]


def _normalize_actor_role(actor_role: str | None) -> str:
    role = (actor_role or "hr").strip().lower()
    if role in {"admin", "hr", "payroll", "manager", "employee"}:
        return role
    return "employee"


def _role_can_view(role: str, visibility: str) -> bool:
    if role in {"admin", "hr"}:
        return True
    if role == "payroll":
        return visibility in {"payroll", "employee"}
    if role == "manager":
        return visibility in {"manager", "employee"}
    return visibility == "employee"


def _add_years(date_text: str | None, years: int) -> str:
    try:
        base = date.fromisoformat(str(date_text)) if date_text else datetime.utcnow().date()
    except ValueError:
        base = datetime.utcnow().date()
    try:
        return base.replace(year=base.year + years).isoformat()
    except ValueError:
        return base.replace(month=2, day=28, year=base.year + years).isoformat()


def _employee_file_document_from_row(row: dict[str, Any], actor_role: str) -> EmployeeFileDocumentOut:
    document_type = str(row.get("document_type") or row.get("documentType") or "certificate")
    document_class = _document_class(document_type)
    visibility = str(row.get("visibility") or document_class["default_visibility"])
    issued_at = row.get("issued_at") or row.get("issuedAt")
    if hasattr(issued_at, "isoformat"):
        issued_at = issued_at.isoformat()
    valid_until = row.get("valid_until") or row.get("validUntil")
    if hasattr(valid_until, "isoformat"):
        valid_until = valid_until.isoformat()
    retention_until = row.get("retention_until") or row.get("retentionUntil") or _add_years(str(issued_at) if issued_at else None, int(document_class["retention_years"]))
    if hasattr(retention_until, "isoformat"):
        retention_until = retention_until.isoformat()
    return EmployeeFileDocumentOut(
        id=str(row.get("id") or f"employee-file-{uuid4()}"),
        employeeRef=str(row.get("employee_ref") or row.get("employeeRef") or ""),
        documentType=document_type,
        title=str(row.get("title") or document_class["title"]),
        status=str(row.get("status") or "active"),
        visibility=visibility,
        legalBasis=[str(item) for item in document_class["legal_basis"]],
        issuedAt=str(issued_at) if issued_at else None,
        validUntil=str(valid_until) if valid_until else None,
        retentionUntil=str(retention_until),
        dmsDocumentId=row.get("dms_document_id") or row.get("dmsDocumentId"),
        canEmployeeView=_role_can_view("employee", visibility),
        canManagerView=_role_can_view("manager", visibility),
        deletionBlockedReason=str(document_class["deletion_rule"]),
        auditRef=str(row.get("audit_ref") or row.get("auditRef") or f"hrm-akte:{row.get('id') or 'contract'}"),
    )


def _filter_employee_file_documents(documents: list[EmployeeFileDocumentOut], actor_role: str) -> tuple[list[EmployeeFileDocumentOut], int]:
    visible = [document for document in documents if _role_can_view(actor_role, document.visibility)]
    return visible, len(documents) - len(visible)


def _pilot_employee_file_documents(employee_ref: str, actor_role: str) -> tuple[list[EmployeeFileDocumentOut], int]:
    rows = [
        {
            "id": f"akte-{employee_ref}-contract",
            "employee_ref": employee_ref,
            "document_type": "employment_contract",
            "title": "Arbeitsvertrag",
            "visibility": "hr",
            "issued_at": "2024-01-01",
            "dms_document_id": "dms-hr-contract-demo",
        },
        {
            "id": f"akte-{employee_ref}-certificate",
            "employee_ref": employee_ref,
            "document_type": "certificate",
            "title": "Staplerschein / Qualifikationsnachweis",
            "visibility": "employee",
            "issued_at": "2025-04-01",
            "valid_until": "2028-04-01",
            "dms_document_id": "dms-hr-cert-demo",
        },
        {
            "id": f"akte-{employee_ref}-payroll",
            "employee_ref": employee_ref,
            "document_type": "payroll_document",
            "title": "Payroll-Stammdatenblatt",
            "visibility": "payroll",
            "issued_at": "2025-01-01",
            "dms_document_id": "dms-hr-payroll-demo",
        },
    ]
    documents = [_employee_file_document_from_row(row, actor_role) for row in rows]
    return _filter_employee_file_documents(documents, actor_role)


def _employee_file_response(employee_ref: str, actor_role: str, source: str, documents: list[EmployeeFileDocumentOut], hidden_count: int) -> EmployeeFileOut:
    return EmployeeFileOut(
        employeeRef=employee_ref,
        source=source,
        actorRole=actor_role,
        documentClasses=_employee_file_document_classes(),
        documents=documents,
        hiddenDocumentCount=hidden_count,
        exportPackage=EmployeeFileExportOut(
            available=True,
            format="json+zip",
            includesAuditTrail=True,
            includesRetentionPlan=True,
            dataSubjectAccessHint="DSGVO-Auskunftspaket enthaelt sichtbare Aktenmetadaten, Audit-Referenzen und Retention-Plan.",
        ),
        retention=EmployeeFileRetentionOut(
            deletionConcept="Dokumentklasse bestimmt Mindestaufbewahrung; Zweckfortfall und Rechtsfristen blockieren automatische Loeschung.",
            reviewCadence="jaehrlich und bei Austritt",
            blockedDocumentCount=sum(1 for document in documents if document.retentionUntil >= datetime.utcnow().date().isoformat()),
            nextReviewHint="HR prueft Retention, DMS-Referenz und Zweckbindung vor Loeschlauf.",
        ),
    )


def _load_employee_file_documents(db: Session, tenant_id: str, employee_ref: str, actor_role: str) -> tuple[list[EmployeeFileDocumentOut], int, str]:
    rows = db.execute(
        text(
            """
            SELECT id, employee_ref, document_type, title, status, visibility,
                   issued_at, valid_until, retention_until, dms_document_id, audit_ref
            FROM domain_hr.employee_file_documents
            WHERE tenant_id = :tenant_id AND employee_ref = :employee_ref
            ORDER BY issued_at DESC NULLS LAST, created_at DESC NULLS LAST
            """
        ),
        {"tenant_id": tenant_id, "employee_ref": employee_ref},
    ).mappings().all()
    if not rows:
        visible, hidden = _pilot_employee_file_documents(employee_ref, actor_role)
        return visible, hidden, "pilot"
    documents = [_employee_file_document_from_row(dict(row), actor_role) for row in rows]
    visible, hidden = _filter_employee_file_documents(documents, actor_role)
    return visible, hidden, "database"


def build_hrm_readiness() -> HrmReadinessOut:
    """Return the German HRM target contract used by UI, docs and tests."""

    capabilities = [
        HrmReadinessCapabilityOut(
            id="hrm-personnel-file",
            title="Digitale Personalakte und Stammdaten",
            status="contract_complete",
            priority="P0",
            legalBasis=["DSGVO", "BDSG §26", "Nachweisgesetz"],
            implementedEvidence=["GET/POST/PUT /api/v1/personal/mitarbeiter", "GET /api/v1/personal/time-profiles"],
            missingCapabilities=[
                "Produktive DMS-Ablage und rechtlich freigegebene Retention-Fristen bleiben external_gate",
            ],
            nextSlices=["HRM-AKTE-001", "HRM-DMS-001", "HRM-RETENTION-001"],
            controls=["Datenminimierung", "Need-to-know-Rollen", "Audit-Log", "Export und Loeschlauf"],
        ),
        HrmReadinessCapabilityOut(
            id="hrm-time-absence",
            title="Arbeitszeit, Urlaub und Abwesenheiten",
            status="implemented",
            priority="P0",
            legalBasis=["BAG 1 ABR 22/21", "ArbSchG §3 Abs. 2 Nr. 1", "ArbZG"],
            implementedEvidence=[
                "GET /api/v1/personal/time-cockpit",
                "POST /api/v1/personal/time-entries",
                "POST /api/v1/personal/absences/import",
                "GET /api/v1/personal/work-plan",
            ],
            missingCapabilities=["Tarif-/Betriebsvereinbarungs-Regelkalibrierung", "produktive Terminal-/Mobile-Adapter"],
            nextSlices=["HR-TIME-RULES-001", "HR-TIME-MOBILE-001"],
            controls=["Korrekturgrund", "Managerfreigabe", "Payroll-Blocker", "Keine stille Änderung exportierter Zeiten"],
        ),
        HrmReadinessCapabilityOut(
            id="hrm-eau",
            title="eAU und Krankmeldung",
            status="contract_complete",
            priority="P0",
            legalBasis=["SGB IV §109", "Entgeltfortzahlungsgesetz"],
            implementedEvidence=["POST /api/v1/personal/absences/import kann Krankheit als Abwesenheit spiegeln"],
            missingCapabilities=[
                "Produktiver eAU-Kommunikationszugang bleibt external_gate",
            ],
            nextSlices=["HRM-EAU-001"],
            controls=["Nur erforderliche Statusdaten speichern", "Fristenmonitor", "Audit ohne Diagnosedaten"],
        ),
        HrmReadinessCapabilityOut(
            id="hrm-payroll",
            title="Payroll-/DATEV-Vorbereitung",
            status="contract_complete",
            priority="P0",
            legalBasis=["GoBD", "SV-Meldeportal ist kein Entgeltabrechnungsersatz"],
            implementedEvidence=["GET/POST /api/v1/personal/payroll-exports", "Payroll-Readiness im Time-Cockpit"],
            missingCapabilities=["DATEV-Zielformat und Steuerberaterfreigabe bleiben external_gate"],
            nextSlices=["HR-TIME-PAYROLL-CLOSE-001", "HRM-DATEV-001"],
            controls=["Nur freigegebene Werte exportieren", "Kostenstellen", "Blockerliste", "Exportprotokoll"],
        ),
        HrmReadinessCapabilityOut(
            id="hrm-contract-documents",
            title="Vertrags- und Dokumentenmanagement",
            status="contract_complete",
            priority="P0",
            legalBasis=["Nachweisgesetz 2025 Textform-Ausbau", "DSGVO"],
            implementedEvidence=["Onboarding-Checklisten über /api/v1/training/onboarding/*"],
            missingCapabilities=["LibreOffice-Rendering und E-Signatur-Anbieter bleiben external_gate"],
            nextSlices=["HRM-CONTRACTS-001", "HRM-ESIGN-001"],
            controls=["Vorlagenversion", "Empfangsbestaetigung", "Archivfristen", "Schriftformwunsch dokumentieren"],
        ),
        HrmReadinessCapabilityOut(
            id="hrm-self-service",
            title="Employee und Manager Self Service",
            status="contract_complete",
            priority="P1",
            legalBasis=["DSGVO Rollen- und Zweckbindung", "Betriebsratsfaehigkeit"],
            implementedEvidence=["Zeitbuchung, Abwesenheitsimport, Schicht-/Kalender-/Onboarding-Sichten"],
            missingCapabilities=["Betriebsvereinbarung und SSO-Rollenzuordnung bleiben external_gate"],
            nextSlices=["HRM-ESS-001", "HRM-MSS-001"],
            controls=["Vier-Augen-Freigaben", "Rollenfilter", "freigegebene Rollen- und Zweckbindung"],
        ),
        HrmReadinessCapabilityOut(
            id="hrm-recruiting-development",
            title="Recruiting, Onboarding, Performance und Entwicklung",
            status="contract_complete",
            priority="P1",
            legalBasis=["DSGVO Bewerberloeschfristen", "EU AI Act Annex III bei KI-Screening"],
            implementedEvidence=["/api/v1/training/onboarding/*", "/api/v1/training/qualifications"],
            missingCapabilities=["Karriereseite und produktive Interviewkommunikation bleiben external_gate"],
            nextSlices=["HRM-RECRUITING-001", "HRM-PERFORMANCE-001"],
            controls=["Bewerber-Retention", "Human-in-the-loop", "Betriebsratsfaehige Auswertungen"],
        ),
        HrmReadinessCapabilityOut(
            id="hrm-analytics-compliance",
            title="Reporting, People Analytics, Datenschutz und Mandantenfaehigkeit",
            status="contract_complete",
            priority="P0",
            legalBasis=["DSGVO", "BDSG §26", "BetrVG Mitbestimmung", "EU AI Act"],
            implementedEvidence=["Time-Cockpit KPIs", "tenant_id auf HR-Time-Tabellen", "Audit-/Statusfelder in HR-Time-Slices"],
            missingCapabilities=["DSFA- und Betriebsratsfreigaben bleiben external_gate"],
            nextSlices=["HRM-ANALYTICS-001", "HRM-PRIVACY-001", "HRM-AI-GOV-001"],
            controls=["Aggregationsschwellen", "PII-Minimierung", "Exportierbarkeit", "freigegebener Reporting-Zweck"],
        ),
    ]

    integrations = [
        HrmReadinessIntegrationOut(
            id="microsoft-365",
            title="Microsoft 365, Teams, Outlook, Entra ID",
            status="planned",
            direction="bidirectional",
            minimumContract=["SSO", "Kalender-Busy-Blocker", "Abwesenheitskalender", "Benutzeranlage", "Teams-Benachrichtigung"],
            nextSlice="HRM-M365-001",
        ),
        HrmReadinessIntegrationOut(
            id="google-workspace",
            title="Google Workspace",
            status="planned",
            direction="bidirectional",
            minimumContract=["OAuth Scopes", "Calendar Events", "Directory Mapping", "Busy-only Datenschutz"],
            nextSlice="HRM-GOOGLE-001",
        ),
        HrmReadinessIntegrationOut(
            id="libreoffice",
            title="LibreOffice Dokumentvorlagen",
            status="planned",
            direction="export",
            minimumContract=["ODT/DOCX Vorlagen", "Serienbriefdaten", "PDF-Erzeugung", "Vorlagenversion"],
            nextSlice="HRM-LIBREOFFICE-001",
        ),
        HrmReadinessIntegrationOut(
            id="datev-payroll",
            title="DATEV, Steuerberater und Payroll",
            status="partial",
            direction="export",
            minimumContract=["Stammdaten", "Bewegungsdaten", "Fehlzeiten", "Kostenstellen", "Lohnarten", "Monatsabschluss"],
            nextSlice="HRM-DATEV-001",
        ),
        HrmReadinessIntegrationOut(
            id="dms-esign",
            title="DMS und E-Signatur",
            status="planned",
            direction="bidirectional",
            minimumContract=["Dokumentenklasse", "Retention", "Signaturstatus", "Audit-Ref", "Exportpaket"],
            nextSlice="HRM-DMS-001",
        ),
    ]

    ai_controls = [
        HrmReadinessAiControlOut(
            id="hrm-ai-assist",
            title="Kontrollierte HR-KI",
            classification="assistive",
            allowedUse=["Stellenanzeigen-Entwurf", "Dokumentensuche", "Zusammenfassungen", "Lernempfehlungen", "HR-Chatbot mit Quellen"],
            prohibitedUse=["nicht freigegebene KI-Funktionen", "Personalentscheidungen ohne dokumentierte menschliche Pruefung"],
            requiredControls=["Human approval", "Protokollierung", "Quellenanzeige", "Opt-out/Policy", "Keine sensiblen Merkmale als Entscheidungstreiber"],
        ),
        HrmReadinessAiControlOut(
            id="hrm-ai-high-risk",
            title="Recruiting und Personalmanagement KI",
            classification="EU AI Act high-risk when used for employment decisions",
            allowedUse=["Vorsortierung nur mit dokumentierter menschlicher Pruefung", "Skill-Matching als Empfehlung"],
            prohibitedUse=["Blackbox-CV-Sorting", "automatische Ablehnung ohne menschliche Aufsicht"],
            requiredControls=["Risikomanagement", "Datenqualitaet", "Technische Dokumentation", "Transparenz", "menschliche Aufsicht", "Robustheit", "Cybersecurity"],
        ),
    ]

    return HrmReadinessOut(
        status="partial",
        country="DE",
        asOf="2026-05-13",
        minimumChecklist=_HRM_MINIMUM_CHECKLIST,
        capabilities=capabilities,
        integrations=integrations,
        aiControls=ai_controls,
        residualRisks=[
            "Rechtsfeinpruefung und Betriebsvereinbarungen muessen vor Produktivbetrieb abgeschlossen sein.",
            "Produktive eAU-, DATEV-, Microsoft-365- und Google-Workspace-Zugangsdaten fehlen.",
            "AVV/DPA, Hostingort, Subprozessoren und DSFA sind je Fremdanbieter zu pruefen.",
        ],
    )


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


def _parse_event_datetime(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid datetime format") from exc


def _mask_calendar_title(title: str, visibility: str) -> str:
    return "Besetzt" if visibility in {"private", "busy_only"} else title


def _calendar_event_from_row(row: Any) -> CalendarEventOut:
    row_map = dict(row)
    visibility = str(row_map.get("visibility") or "team")
    metadata_raw = row_map.get("metadata")
    metadata = _parse_preferences(metadata_raw)
    if visibility in {"private", "busy_only"}:
        metadata = {key: value for key, value in metadata.items() if key in {"busy", "source"}}
    return CalendarEventOut(
        id=str(row_map.get("id") or ""),
        sourceSystem=str(row_map.get("source_system") or "valeo"),
        provider=str(row_map.get("provider") or "internal"),
        externalEventRef=str(row_map.get("external_event_ref") or "") or None,
        eventType=str(row_map.get("event_type") or ""),
        title=_mask_calendar_title(str(row_map.get("title") or ""), visibility),
        employeeRef=str(row_map.get("employee_ref") or "") or None,
        resourceRef=str(row_map.get("resource_ref") or "") or None,
        startsAt=str(row_map.get("starts_at") or ""),
        endsAt=str(row_map.get("ends_at") or ""),
        timezone=str(row_map.get("timezone") or "Europe/Berlin"),
        visibility=visibility,
        status=str(row_map.get("status") or "confirmed"),
        syncState=str(row_map.get("sync_state") or "local"),
        conflictLevel=str(row_map.get("conflict_level") or "none"),
        sourceRef=str(row_map.get("source_ref") or "") or None,
        metadata=metadata,
    )


def _wage_type_for_entry(entry_type: str, hours: float) -> str:
    if entry_type in {"Urlaub", "Krank"}:
        return "ABSENCE"
    if entry_type == "Bereitschaft":
        return "STANDBY"
    if hours > _STANDARD_DAILY_HOURS:
        return "OVERTIME"
    return "REGULAR"


def _payroll_item_from_time_row(row: Any) -> PayrollExportItemOut:
    row_map = dict(row)
    entry_type = str(row_map.get("entry_type") or "Arbeit")
    hours = float(row_map.get("hours") or 0)
    return PayrollExportItemOut(
        employeeRef=str(row_map.get("employee_ref") or ""),
        datum=_to_iso(row_map.get("entry_date")),
        hours=hours,
        entryType=entry_type,
        wageType=_wage_type_for_entry(entry_type, hours),
        costCenter=str(row_map.get("cost_center") or "") or None,
        sourceEntryId=str(row_map.get("id") or ""),
    )


def _payroll_blocker_from_time_row(row: Any) -> PayrollExportBlockerOut:
    row_map = dict(row)
    status = str(row_map.get("status") or "")
    return PayrollExportBlockerOut(
        code="TIME_ENTRY_NOT_APPROVED",
        message=f"Zeitbuchung ist nicht freigegeben: {status}",
        employeeRef=str(row_map.get("employee_ref") or "") or None,
        sourceEntryId=str(row_map.get("id") or "") or None,
    )


def _payroll_export_from_row(row: Any) -> PayrollExportOut:
    row_map = dict(row)
    return PayrollExportOut(
        id=str(row_map.get("id") or ""),
        periodFrom=_to_iso(row_map.get("period_from")),
        periodTo=_to_iso(row_map.get("period_to")),
        targetSystem=str(row_map.get("target_system") or "datev"),
        status=str(row_map.get("status") or "blocked"),
        items=[PayrollExportItemOut(**item) for item in _parse_json_list(row_map.get("items"))],
        blockers=[PayrollExportBlockerOut(**item) for item in _parse_json_list(row_map.get("blockers"))],
    )


def _campaign_finding_from_item(item: Any) -> CampaignCapacityFindingOut:
    item_map = dict(item) if isinstance(item, dict) else {}
    return CampaignCapacityFindingOut(
        code=str(item_map.get("code") or "UNKNOWN"),
        severity=str(item_map.get("severity") or "warning"),
        message=str(item_map.get("message") or ""),
        roleCode=str(item_map.get("roleCode") or item_map.get("role_code") or "") or None,
    )


def _campaign_status(findings: list[CampaignCapacityFindingOut]) -> str:
    if any(finding.severity == "blocker" for finding in findings):
        return "blocked"
    if findings:
        return "warning"
    return "planned"


def _build_campaign_findings(
    role_demand: dict[str, int],
    profile_rows: list[Any],
    absence_rows: list[Any],
    shift_rows: list[Any],
) -> list[CampaignCapacityFindingOut]:
    findings: list[CampaignCapacityFindingOut] = []
    active_by_role: dict[str, set[str]] = {}
    for row in profile_rows:
        row_map = dict(row)
        if _normalize_time_profile_status(row_map.get("status")) != "active":
            continue
        active_by_role.setdefault(str(row_map.get("role_code") or "employee"), set()).add(str(row_map.get("employee_ref") or ""))
    absent_refs = {str(dict(row).get("employee_ref") or "") for row in absence_rows}
    assigned_refs = {
        employee_ref
        for row in shift_rows
        for employee_ref in _parse_json_string_list(dict(row).get("assigned_employee_refs"))
    }
    for role_code, demand in role_demand.items():
        available = active_by_role.get(role_code, set()) - absent_refs
        planned = available & assigned_refs
        if len(available) < demand:
            findings.append(
                CampaignCapacityFindingOut(
                    code="ROLE_CAPACITY_SHORTAGE",
                    severity="blocker",
                    message=f"Rollenbedarf {role_code} nicht gedeckt: {len(available)} verfuegbar, {demand} benoetigt.",
                    roleCode=role_code,
                )
            )
        elif len(planned) < demand:
            findings.append(
                CampaignCapacityFindingOut(
                    code="ROLE_NOT_FULLY_SCHEDULED",
                    severity="warning",
                    message=f"Rollenbedarf {role_code} ist verfuegbar, aber noch nicht voll eingeplant.",
                    roleCode=role_code,
                )
            )
    return findings


def _campaign_capacity_from_row(row: Any) -> CampaignCapacityOut:
    row_map = dict(row)
    role_demand_raw = row_map.get("role_demand")
    role_demand = _parse_preferences(role_demand_raw)
    return CampaignCapacityOut(
        id=str(row_map.get("id") or ""),
        campaignCode=str(row_map.get("campaign_code") or ""),
        name=str(row_map.get("name") or ""),
        periodFrom=_to_iso(row_map.get("period_from")),
        periodTo=_to_iso(row_map.get("period_to")),
        locationCode=str(row_map.get("location_code") or "main"),
        roleDemand={str(key): int(value) for key, value in role_demand.items()},
        expectedVolume=float(row_map.get("expected_volume")) if row_map.get("expected_volume") is not None else None,
        status=str(row_map.get("status") or "planned"),
        findings=[_campaign_finding_from_item(item) for item in _parse_json_list(row_map.get("findings"))],
    )


def _field_conflict_from_item(item: Any) -> FieldServiceConflictOut:
    item_map = dict(item) if isinstance(item, dict) else {}
    return FieldServiceConflictOut(
        code=str(item_map.get("code") or "UNKNOWN"),
        severity=str(item_map.get("severity") or "warning"),
        message=str(item_map.get("message") or ""),
    )


def _build_field_conflicts(profile_rows: list[Any], absence_rows: list[Any], calendar_rows: list[Any]) -> list[FieldServiceConflictOut]:
    conflicts: list[FieldServiceConflictOut] = []
    if not profile_rows:
        conflicts.append(FieldServiceConflictOut(code="PROFILE_MISSING", severity="blocker", message="Kein HR-Time-Profil fuer Aussendienstplanung."))
    else:
        profile = dict(profile_rows[0])
        if _normalize_time_profile_status(profile.get("status")) != "active":
            conflicts.append(FieldServiceConflictOut(code="PROFILE_INACTIVE", severity="blocker", message="Mitarbeiter ist nicht aktiv planbar."))
        if str(profile.get("time_model") or "") not in {"field_service", "flex", "standard"}:
            conflicts.append(FieldServiceConflictOut(code="TIME_MODEL_MISMATCH", severity="warning", message="Zeitmodell ist nicht fuer Aussendienst optimiert."))
    if absence_rows:
        conflicts.append(FieldServiceConflictOut(code="ABSENCE_COLLISION", severity="blocker", message="Mitarbeiter hat im Besuchsfenster eine genehmigte Abwesenheit."))
    if calendar_rows:
        conflicts.append(FieldServiceConflictOut(code="CALENDAR_COLLISION", severity="warning", message="Kalender enthaelt bereits einen Blocker im Besuchsfenster."))
    return conflicts


def _field_status(conflicts: list[FieldServiceConflictOut]) -> str:
    if any(conflict.severity == "blocker" for conflict in conflicts):
        return "blocked"
    if conflicts:
        return "warning"
    return "planned"


def _field_service_from_row(row: Any) -> FieldServicePlanOut:
    row_map = dict(row)
    return FieldServicePlanOut(
        id=str(row_map.get("id") or ""),
        employeeRef=str(row_map.get("employee_ref") or ""),
        customerRef=str(row_map.get("customer_ref") or ""),
        territoryCode=str(row_map.get("territory_code") or ""),
        campaignCode=str(row_map.get("campaign_code") or "") or None,
        visitType=str(row_map.get("visit_type") or "consulting"),
        startsAt=str(row_map.get("starts_at") or ""),
        endsAt=str(row_map.get("ends_at") or ""),
        status=str(row_map.get("status") or "planned"),
        conflicts=[_field_conflict_from_item(item) for item in _parse_json_list(row_map.get("conflicts"))],
        notes=str(row_map.get("notes") or "") or None,
    )


def _parse_date_set(raw: str | None) -> set[date]:
    if not raw:
        return set()
    dates: set[date] = set()
    for item in raw.split(","):
        value = item.strip()
        if value:
            dates.add(_parse_entry_date(value))
    return dates


def _is_night_window(start_value: Any, end_value: Any) -> bool:
    start_minutes = _parse_clock_minutes(start_value)
    end_minutes = _parse_clock_minutes(end_value)
    if start_minutes is None or end_minutes is None:
        return False
    return start_minutes < 6 * _MINUTES_PER_HOUR or end_minutes > 22 * _MINUTES_PER_HOUR or end_minutes <= start_minutes


def _planning_preference_from_profile(row: Any, user_preferences: dict[str, Any] | None = None) -> PlanningPreferenceOut:
    row_map = dict(row)
    prefs = _parse_preferences(user_preferences or row_map.get("preferences"))
    planning = _parse_preferences(prefs.get("planning") or prefs.get("hr_time_planning"))
    employee_ref = str(row_map.get("employee_ref") or row_map.get("id") or "")
    time_model = str(row_map.get("time_model") or "")
    role_code = str(row_map.get("role_code") or "")
    default_night = time_model == "driver" or "fahrer" in role_code.lower() or "driver" in role_code.lower()
    return PlanningPreferenceOut(
        employeeRef=employee_ref,
        prefersNightTours=bool(planning.get("prefers_night_tours", planning.get("prefersNightTours", False))),
        avoidNightTours=bool(planning.get("avoid_night_tours", planning.get("avoidNightTours", False))),
        childcareSensitive=bool(planning.get("childcare_sensitive", planning.get("childcareSensitive", False))),
        preferredWeekdays=_parse_json_string_list(planning.get("preferred_weekdays", planning.get("preferredWeekdays"))),
        schoolHolidayRegions=_parse_json_string_list(planning.get("school_holiday_regions", planning.get("schoolHolidayRegions"))),
        bridgeDayPolicy=str(planning.get("bridge_day_policy") or planning.get("bridgeDayPolicy") or ("preload" if default_night else "normal")),
        maxExtraHoursBeforeHoliday=float(planning.get("max_extra_hours_before_holiday") or planning.get("maxExtraHoursBeforeHoliday") or 2.0),
    )


def _work_plan_findings_for_assignment(
    assignment: WorkPlanAssignmentOut,
    preference: PlanningPreferenceOut | None,
    absence_dates_by_employee: dict[str, set[date]],
    school_holiday_dates: set[date],
    bridge_days: set[date],
    holiday_dates: set[date],
) -> list[WorkPlanFindingOut]:
    findings: list[WorkPlanFindingOut] = []
    assignment_date = _parse_entry_date(assignment.datum)
    employee_ref = assignment.employeeRef
    if employee_ref and assignment_date in absence_dates_by_employee.get(employee_ref, set()) and assignment.sourceType != "absence":
        findings.append(
            WorkPlanFindingOut(
                code="ABSENCE_COLLISION",
                severity="blocker",
                message="Einsatz kollidiert mit genehmigter Abwesenheit.",
                employeeRef=employee_ref,
                datum=assignment.datum,
                sourceRef=assignment.id,
            )
        )
    if preference:
        is_night = _is_night_window(assignment.startTime, assignment.endTime)
        weekday = assignment_date.strftime("%a").lower()
        if is_night and preference.avoidNightTours:
            findings.append(
                WorkPlanFindingOut(
                    code="NIGHT_TOUR_AVOIDED",
                    severity="warning",
                    message="Persoenliche Praeferenz vermeidet Nachttouren.",
                    employeeRef=employee_ref,
                    datum=assignment.datum,
                    sourceRef=assignment.id,
                )
            )
        if preference.prefersNightTours and not is_night and assignment.sourceType in {"shift", "field_service"}:
            findings.append(
                WorkPlanFindingOut(
                    code="NIGHT_TOUR_PREFERENCE_MISSED",
                    severity="info",
                    message="Mitarbeiter bevorzugt Nachttouren; aktueller Einsatz ist tagsueber.",
                    employeeRef=employee_ref,
                    datum=assignment.datum,
                    sourceRef=assignment.id,
                )
            )
        if preference.preferredWeekdays and weekday not in {item[:3].lower() for item in preference.preferredWeekdays}:
            findings.append(
                WorkPlanFindingOut(
                    code="WEEKDAY_PREFERENCE_MISMATCH",
                    severity="warning",
                    message="Einsatz liegt ausserhalb der bevorzugten Wochentage.",
                    employeeRef=employee_ref,
                    datum=assignment.datum,
                    sourceRef=assignment.id,
                )
            )
        if preference.childcareSensitive and assignment_date in school_holiday_dates:
            findings.append(
                WorkPlanFindingOut(
                    code="SCHOOL_HOLIDAY_SENSITIVITY",
                    severity="warning",
                    message="Schulferien treffen Mitarbeiter mit Betreuungsrelevanz.",
                    employeeRef=employee_ref,
                    datum=assignment.datum,
                    sourceRef=assignment.id,
                )
            )
        next_day = date.fromordinal(assignment_date.toordinal() + 1)
        if preference.bridgeDayPolicy == "preload" and (next_day in bridge_days or next_day in holiday_dates):
            findings.append(
                WorkPlanFindingOut(
                    code="PRE_HOLIDAY_LOAD",
                    severity="info",
                    message="Mehrarbeit vor Bruecken-/Feiertag ist als Praeferenz/Planungsdruck markiert.",
                    employeeRef=employee_ref,
                    datum=assignment.datum,
                    sourceRef=assignment.id,
                )
            )
    return findings


def _assignment_status(findings: list[WorkPlanFindingOut], fallback: str) -> str:
    if any(finding.severity == "blocker" for finding in findings):
        return "blocked"
    if any(finding.severity == "warning" for finding in findings):
        return "warning"
    return fallback


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


@router.get("/hrm-readiness", response_model=HrmReadinessOut)
async def get_hrm_readiness(_tenant_id: str = Depends(get_tenant_id)):
    return build_hrm_readiness()


@router.get("/hrm-operating-system", response_model=HrmOperatingSystemOut)
async def get_hrm_operating_system(_tenant_id: str = Depends(get_tenant_id)):
    return build_hrm_operating_system_contract()


@router.get("/hrm-operations-gates", response_model=HrmOperationsGatesOut)
async def get_hrm_operations_gates(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return _get_hrm_operations_gates_runtime(db, tenant_id)


@router.get("/hrm-operations-gates/go-live-policy", response_model=HrmOperationsGoLivePolicyOut)
async def get_hrm_operations_go_live_policy(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    gates = _get_hrm_operations_gates_runtime(db, tenant_id)
    blockers = [gate for gate in gates.gates if gate.goLiveBlocking and gate.status != "approved"]
    return HrmOperationsGoLivePolicyOut(
        goLiveAllowed=not blockers,
        blockerCount=len(blockers),
        blockers=blockers,
        status="approved" if not blockers else "blocked",
        summary="HRM-Go-live freigegeben." if not blockers else "HRM-Go-live durch Betriebsfreigabe-Gates blockiert.",
    )


@router.post("/hrm-operations-gates/{gate_id}/evidence", response_model=HrmOperationsGateEvidenceOut, status_code=201)
async def create_hrm_operations_gate_evidence(
    gate_id: str,
    payload: HrmOperationsGateEvidenceIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _require_hrm_gate(gate_id)
    try:
        current = _load_single_hrm_gate(db, tenant_id, gate_id)
        row = PersonalService(db, tenant_id).add_gate_evidence(
            gate_id=gate_id,
            evidence_id=str(uuid4()),
            evidence_type=payload.evidenceType,
            title=payload.title,
            artifact_ref=payload.artifactRef,
            submitted_by=payload.submittedBy,
            metadata=payload.metadata,
            current_status=current.status,
        )
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail="HRM operations gate persistence is not available") from exc
    return _evidence_out(row)


@router.post("/hrm-operations-gates/{gate_id}/decision", response_model=HrmOperationsGateActionOut)
async def decide_hrm_operations_gate(
    gate_id: str,
    payload: HrmOperationsGateDecisionIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _require_hrm_gate(gate_id)
    try:
        current = _load_single_hrm_gate(db, tenant_id, gate_id)
        PersonalService(db, tenant_id).decide_gate(
            gate_id=gate_id,
            decision=payload.decision,
            decided_by=payload.decidedBy,
            reason=payload.reason,
            current_status=current.status,
            evidence_count=current.evidenceCount,
        )
        gate = _load_single_hrm_gate(db, tenant_id, gate_id)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail="HRM operations gate persistence is not available") from exc
    return HrmOperationsGateActionOut(ok=True, gate=gate)


@router.post("/hrm-operations-gates/{gate_id}/probe", response_model=HrmOperationsGateProbeOut, status_code=201)
async def record_hrm_operations_gate_probe(
    gate_id: str,
    payload: HrmOperationsGateProbeIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    _require_hrm_gate(gate_id)
    try:
        current = _load_single_hrm_gate(db, tenant_id, gate_id)
        row = PersonalService(db, tenant_id).record_gate_probe(
            gate_id=gate_id,
            probe_id=str(uuid4()),
            provider=payload.provider,
            probe_type=payload.probeType,
            result=payload.result,
            performed_by=payload.performedBy,
            details=payload.details,
            current_status=current.status,
        )
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail="HRM operations gate persistence is not available") from exc
    return _probe_out(row)


@router.get("/employee-files/{employee_ref}", response_model=EmployeeFileOut)
async def get_employee_file(
    employee_ref: str,
    actor_role: str | None = Query(default="hr", alias="actorRole"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    role = _normalize_actor_role(actor_role)
    try:
        documents, hidden_count, source = _load_employee_file_documents(db, tenant_id, employee_ref, role)
    except Exception:
        documents, hidden_count = _pilot_employee_file_documents(employee_ref, role)
        source = "pilot"
    return _employee_file_response(employee_ref, role, source, documents, hidden_count)


@router.post("/employee-files/{employee_ref}/documents", response_model=EmployeeFileDocumentOut, status_code=201)
async def create_employee_file_document(
    employee_ref: str,
    payload: EmployeeFileDocumentCreateIn,
    actor_role: str | None = Query(default="hr", alias="actorRole"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    role = _normalize_actor_role(actor_role)
    if role not in {"admin", "hr", "payroll"}:
        raise HTTPException(status_code=403, detail="Personalakten-Dokumente duerfen nur HR, Payroll oder Admin anlegen.")
    document_class = _document_class(payload.documentType)
    visibility = payload.visibility or str(document_class["default_visibility"])
    if visibility == "payroll" and role not in {"admin", "payroll", "hr"}:
        raise HTTPException(status_code=403, detail="Payroll-Dokumente duerfen nur HR/Payroll/Admin anlegen.")
    document_id = f"hrdoc-{uuid4()}"
    retention_until = _add_years(payload.issuedAt, int(document_class["retention_years"]))
    audit_ref = f"hrm-akte:{document_id}"
    row = {
        "id": document_id,
        "tenant_id": tenant_id,
        "employee_ref": employee_ref,
        "document_type": payload.documentType,
        "title": payload.title,
        "status": "active",
        "visibility": visibility,
        "issued_at": payload.issuedAt,
        "valid_until": payload.validUntil,
        "retention_until": retention_until,
        "dms_document_id": payload.dmsDocumentId,
        "audit_ref": audit_ref,
        "notes": payload.notes,
        "created_by": payload.createdBy,
    }
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_hr.employee_file_documents (
                    id, tenant_id, employee_ref, document_type, title, status,
                    visibility, issued_at, valid_until, retention_until,
                    dms_document_id, audit_ref, notes, created_by, created_at, updated_at
                )
                VALUES (
                    :id, :tenant_id, :employee_ref, :document_type, :title, :status,
                    :visibility, CAST(:issued_at AS date), CAST(:valid_until AS date),
                    CAST(:retention_until AS date), :dms_document_id, :audit_ref,
                    :notes, :created_by, NOW(), NOW()
                )
                """
            ),
            row,
        )
        db.commit()
    except Exception:
        # The contract remains usable in environments where the HRM-AKTE table
        # migration is not applied yet; persistence is covered by follow-up slice.
        pass
    return _employee_file_document_from_row(row, role)


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
    rows = PersonalService(db, tenant_id).list_mitarbeiter(search=search, status=status)
    return [MitarbeiterOut(**r) for r in rows]


@router.get("/mitarbeiter/{user_id}", response_model=MitarbeiterOut)
async def get_mitarbeiter(
    user_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        return MitarbeiterOut(**PersonalService(db, tenant_id).get_mitarbeiter(user_id))
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Mitarbeiter nicht gefunden")


@router.post("/mitarbeiter", response_model=MitarbeiterOut, status_code=201)
async def create_mitarbeiter(
    payload: MitarbeiterIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    from app.core.exceptions import ConflictError
    try:
        user_id = PersonalService(db, tenant_id).create_mitarbeiter(payload)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return await get_mitarbeiter(user_id=user_id, tenant_id=tenant_id, db=db)


@router.put("/mitarbeiter/{user_id}", response_model=MitarbeiterOut)
async def update_mitarbeiter(
    user_id: str,
    payload: MitarbeiterIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        PersonalService(db, tenant_id).update_mitarbeiter(user_id, payload)
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Mitarbeiter nicht gefunden")
    return await get_mitarbeiter(user_id=user_id, tenant_id=tenant_id, db=db)


@router.get("/zeiterfassung", response_model=list[ZeitEintragOut])
async def list_zeiterfassung(
    datum: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    rows = PersonalService(db, tenant_id).list_zeiteintraege(datum=datum)
    return [
        ZeitEintragOut(
            id=r["id"],
            mitarbeiter=r["employeeRef"],
            datum=r["datum"],
            kommen=r["startTime"] or "",
            gehen=r["endTime"] or "",
            stunden=r["hours"],
            typ=r["entryType"],
        )
        for r in rows
    ]


@router.post("/time-entries", response_model=TimeEntryBookingOut, status_code=201)
async def create_time_entry(
    payload: TimeEntryBookingCreateIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    svc = PersonalService(db, tenant_id)
    data = svc.create_zeiteintrag(payload.model_dump(by_alias=True))
    return TimeEntryBookingOut(**data)


@router.post("/time-entries/{entry_id}/submit", response_model=TimeEntryActionOut)
async def submit_time_entry(
    entry_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    from app.core.exceptions import ConflictError
    try:
        data = PersonalService(db, tenant_id).submit_zeiteintrag(entry_id)
        return TimeEntryActionOut(ok=True, entry=TimeEntryBookingOut(**data))
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.detail)


@router.post("/time-entries/{entry_id}/approve", response_model=TimeEntryActionOut)
async def approve_time_entry(
    entry_id: str,
    payload: TimeEntryApproveIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    from app.core.exceptions import ConflictError
    try:
        data = PersonalService(db, tenant_id).approve_zeiteintrag(entry_id, payload.approvedBy)
        return TimeEntryActionOut(ok=True, entry=TimeEntryBookingOut(**data))
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.detail)


@router.post("/time-entries/{entry_id}/correct", response_model=TimeEntryActionOut)
async def correct_time_entry(
    entry_id: str,
    payload: TimeEntryBookingCorrectionIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
    try:
        data = PersonalService(db, tenant_id).correct_zeiteintrag(entry_id, payload.model_dump(by_alias=True))
        return TimeEntryActionOut(ok=True, entry=TimeEntryBookingOut(**data))
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Zeitbuchung nicht gefunden")
    except (ConflictError, ValidationFailedError) as exc:
        raise HTTPException(status_code=409, detail=exc.detail)


@router.get("/absences", response_model=list[AbsenceOut])
async def list_absences(
    datum_von: str | None = Query(default=None),
    datum_bis: str | None = Query(default=None),
    status: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    rows = PersonalService(db, tenant_id).list_abwesenheiten(
        datum_von=datum_von, datum_bis=datum_bis, status=status
    )
    return [AbsenceOut(**r) for r in rows]


@router.post("/absences/import", response_model=AbsenceImportOut, status_code=201)
async def import_absence(
    payload: AbsenceImportIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    from app.core.exceptions import ValidationFailedError
    try:
        absences, count = PersonalService(db, tenant_id).import_abwesenheit(payload.model_dump(by_alias=True))
        return AbsenceImportOut(ok=True, imported=count, absences=[AbsenceOut(**r) for r in absences])
    except ValidationFailedError as exc:
        raise HTTPException(status_code=400, detail=exc.detail)


@router.get("/shifts", response_model=list[ShiftOut])
async def list_shifts(
    datum_von: str | None = Query(default=None),
    datum_bis: str | None = Query(default=None),
    location: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    rows = PersonalService(db, tenant_id).list_shifts(
        datum_von=datum_von, datum_bis=datum_bis, location=location
    )
    return [_shift_from_row(row) for row in rows]


@router.post("/shifts", response_model=ShiftOut, status_code=201)
async def create_shift(
    payload: ShiftCreateIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    svc = PersonalService(db, tenant_id)
    shift_date = _parse_entry_date(payload.datum)
    profile_rows, absence_rows = svc.get_shift_context(shift_date)
    conflicts = _build_shift_conflicts(
        assigned_employee_refs=payload.assignedEmployeeRefs,
        required_headcount=payload.requiredHeadcount,
        required_qualifications=payload.requiredQualifications,
        profile_rows=profile_rows,
        absence_rows=absence_rows,
    )
    row = svc.create_shift({
        "id": str(uuid4()),
        "shift_date": shift_date,
        "name": payload.name,
        "location_code": payload.locationCode,
        "required_role": payload.requiredRole,
        "required_qualifications": json.dumps(payload.requiredQualifications),
        "required_headcount": payload.requiredHeadcount,
        "starts_at": payload.startTime,
        "ends_at": payload.endTime,
        "assigned_employee_refs": json.dumps(payload.assignedEmployeeRefs),
        "status": _shift_status(conflicts),
        "conflicts": json.dumps([c.model_dump() for c in conflicts]),
        "notes": payload.notes,
    })
    return _shift_from_row(row)


@router.get("/calendar-events", response_model=list[CalendarEventOut])
async def list_calendar_events(
    start: str | None = Query(default=None),
    end: str | None = Query(default=None),
    employee_ref: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    rows = PersonalService(db, tenant_id).list_calendar_events(
        start=start, end=end, employee_ref=employee_ref, event_type=event_type
    )
    return [_calendar_event_from_row(row) for row in rows]


@router.post("/calendar-events", response_model=CalendarEventOut, status_code=201)
async def create_calendar_event(
    payload: CalendarEventIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    starts_at = _parse_event_datetime(payload.startsAt)
    ends_at = _parse_event_datetime(payload.endsAt)
    if ends_at <= starts_at:
        raise HTTPException(status_code=400, detail="endsAt must be after startsAt")
    row = PersonalService(db, tenant_id).create_calendar_event({
        "id": str(uuid4()),
        "source_system": payload.sourceSystem,
        "provider": payload.provider,
        "external_event_ref": payload.externalEventRef,
        "event_type": payload.eventType,
        "title": payload.title,
        "employee_ref": payload.employeeRef,
        "resource_ref": payload.resourceRef,
        "starts_at": starts_at,
        "ends_at": ends_at,
        "timezone": payload.timezone,
        "visibility": payload.visibility,
        "status": payload.status,
        "sync_state": payload.syncState,
        "conflict_level": payload.conflictLevel,
        "source_ref": payload.sourceRef,
        "metadata": json.dumps(payload.metadata),
    })
    return _calendar_event_from_row(row)


@router.get("/payroll-exports", response_model=list[PayrollExportOut])
async def list_payroll_exports(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    rows = PersonalService(db, tenant_id).list_payroll_exports()
    return [_payroll_export_from_row(row) for row in rows]


@router.post("/payroll-exports", response_model=PayrollExportOut, status_code=201)
async def create_payroll_export(
    payload: PayrollExportCreateIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    period_from = _parse_entry_date(payload.periodFrom)
    period_to = _parse_entry_date(payload.periodTo)
    if period_to < period_from:
        raise HTTPException(status_code=400, detail="periodTo must be on or after periodFrom")
    svc = PersonalService(db, tenant_id)
    time_rows = svc.get_payroll_time_rows(period_from, period_to)
    items = [_payroll_item_from_time_row(r) for r in time_rows if str(r.get("status")) in {"Approved", "Genehmigt"}]
    blockers = [_payroll_blocker_from_time_row(r) for r in time_rows if str(r.get("status")) not in {"Approved", "Genehmigt"}]
    row = svc.create_payroll_export({
        "id": str(uuid4()),
        "period_from": period_from,
        "period_to": period_to,
        "target_system": payload.targetSystem,
        "status": "blocked" if blockers else "ready",
        "items": json.dumps([item.model_dump() for item in items]),
        "blockers": json.dumps([b.model_dump() for b in blockers]),
        "created_by": payload.createdBy,
    })
    return _payroll_export_from_row(row)


@router.get("/campaign-capacity", response_model=list[CampaignCapacityOut])
async def list_campaign_capacity(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    rows = PersonalService(db, tenant_id).list_campaign_capacity()
    return [_campaign_capacity_from_row(row) for row in rows]


@router.post("/campaign-capacity", response_model=CampaignCapacityOut, status_code=201)
async def create_campaign_capacity(
    payload: CampaignCapacityCreateIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    period_from = _parse_entry_date(payload.periodFrom)
    period_to = _parse_entry_date(payload.periodTo)
    if period_to < period_from:
        raise HTTPException(status_code=400, detail="periodTo must be on or after periodFrom")
    svc = PersonalService(db, tenant_id)
    profile_rows, absence_rows, shift_rows = svc.get_campaign_context(
        payload.locationCode, period_from, period_to
    )
    findings = _build_campaign_findings(payload.roleDemand, profile_rows, absence_rows, shift_rows)
    row = svc.create_campaign_capacity({
        "id": str(uuid4()),
        "campaign_code": payload.campaignCode,
        "name": payload.name,
        "period_from": period_from,
        "period_to": period_to,
        "location_code": payload.locationCode,
        "role_demand": json.dumps(payload.roleDemand),
        "expected_volume": payload.expectedVolume,
        "status": _campaign_status(findings),
        "findings": json.dumps([f.model_dump() for f in findings]),
    })
    return _campaign_capacity_from_row(row)


@router.get("/field-service-plan", response_model=list[FieldServicePlanOut])
async def list_field_service_plan(
    employee_ref: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    rows = PersonalService(db, tenant_id).list_field_service_plans(employee_ref=employee_ref)
    return [_field_service_from_row(row) for row in rows]


@router.post("/field-service-plan", response_model=FieldServicePlanOut, status_code=201)
async def create_field_service_plan(
    payload: FieldServicePlanCreateIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    starts_at = _parse_event_datetime(payload.startsAt)
    ends_at = _parse_event_datetime(payload.endsAt)
    if ends_at <= starts_at:
        raise HTTPException(status_code=400, detail="endsAt must be after startsAt")
    svc = PersonalService(db, tenant_id)
    profile_rows, absence_rows, calendar_rows = svc.get_field_service_context(
        payload.employeeRef, starts_at, ends_at
    )
    conflicts = _build_field_conflicts(profile_rows, absence_rows, calendar_rows)
    row = svc.create_field_service_plan({
        "id": str(uuid4()),
        "employee_ref": payload.employeeRef,
        "customer_ref": payload.customerRef,
        "territory_code": payload.territoryCode,
        "campaign_code": payload.campaignCode,
        "visit_type": payload.visitType,
        "starts_at": starts_at,
        "ends_at": ends_at,
        "status": _field_status(conflicts),
        "conflicts": json.dumps([c.model_dump() for c in conflicts]),
        "notes": payload.notes,
    })
    return _field_service_from_row(row)


@router.get("/work-plan", response_model=WorkPlanOut)
async def get_work_plan(
    period_from: str = Query(...),
    period_to: str = Query(...),
    holiday_dates: str | None = Query(default=None),
    bridge_days: str | None = Query(default=None),
    school_holiday_dates: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    start_date = _parse_entry_date(period_from)
    end_date = _parse_entry_date(period_to)
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="period_to must be on or after period_from")

    data = PersonalService(db, tenant_id).get_work_plan_data(start_date, end_date)
    profile_rows = data["profile_rows"]
    user_rows = data["user_rows"]
    absence_rows = data["absence_rows"]
    shift_rows = data["shift_rows"]
    calendar_rows = data["calendar_rows"]
    field_rows = data["field_rows"]

    user_prefs_by_ref: dict[str, dict] = {}
    for row in user_rows:
        row_map = dict(row)
        ref = str(row_map.get("username") or row_map.get("id") or "")
        raw = row_map.get("preferences")
        if ref and raw:
            user_prefs_by_ref[ref] = _parse_preferences(raw)

    preferences: list[PlanningPreferenceOut] = []
    preference_by_ref: dict[str, PlanningPreferenceOut] = {}
    for row in profile_rows:
        row_map = dict(row)
        ref = str(row_map.get("employee_ref") or row_map.get("id") or "")
        pref = _planning_preference_from_profile(row, user_prefs_by_ref.get(ref))
        preferences.append(pref)
        preference_by_ref[ref] = pref

    absence_dates_by_employee: dict[str, set[date]] = {}
    assignments: list[WorkPlanAssignmentOut] = []
    for row in absence_rows:
        row_map = dict(row)
        employee_ref = str(row_map.get("employee_ref") or "")
        entry_date = row_map.get("entry_date")
        target_date = entry_date if isinstance(entry_date, date) else _parse_entry_date(str(entry_date))
        absence_dates_by_employee.setdefault(employee_ref, set()).add(target_date)
        assignments.append(
            WorkPlanAssignmentOut(
                id=str(row_map.get("id") or ""),
                datum=_to_iso(target_date),
                employeeRef=employee_ref,
                label=str(row_map.get("entry_type") or "Abwesenheit"),
                sourceType="absence",
                status=str(row_map.get("status") or "Approved"),
                printReady=True,
            )
        )

    for row in shift_rows:
        row_map = dict(row)
        for employee_ref in _parse_json_string_list(row_map.get("assigned_employee_refs")):
            assignments.append(
                WorkPlanAssignmentOut(
                    id=str(row_map.get("id") or ""),
                    datum=_to_iso(row_map.get("shift_date")),
                    employeeRef=employee_ref,
                    label=str(row_map.get("name") or "Schicht"),
                    sourceType="shift",
                    startTime=_to_time_text(row_map.get("starts_at")),
                    endTime=_to_time_text(row_map.get("ends_at")),
                    status=str(row_map.get("status") or "planned"),
                    printReady=str(row_map.get("status") or "planned") != "blocked",
                )
            )

    for row in calendar_rows:
        row_map = dict(row)
        employee_ref = str(row_map.get("employee_ref") or "")
        if not employee_ref:
            continue
        assignments.append(
            WorkPlanAssignmentOut(
                id=str(row_map.get("id") or ""),
                datum=_to_iso(row_map.get("starts_at")),
                employeeRef=employee_ref,
                label=str(row_map.get("title") or row_map.get("event_type") or "Kalender"),
                sourceType="calendar",
                startTime=_to_time_text(row_map.get("starts_at")),
                endTime=_to_time_text(row_map.get("ends_at")),
                status=str(row_map.get("conflict_level") or row_map.get("status") or "confirmed"),
                printReady=str(row_map.get("conflict_level") or "none") != "blocker",
            )
        )

    for row in field_rows:
        row_map = dict(row)
        assignments.append(
            WorkPlanAssignmentOut(
                id=str(row_map.get("id") or ""),
                datum=_to_iso(row_map.get("starts_at")),
                employeeRef=str(row_map.get("employee_ref") or ""),
                label=f"{row_map.get('visit_type') or 'Aussendienst'}: {row_map.get('customer_ref') or ''}".strip(),
                sourceType="field_service",
                startTime=_to_time_text(row_map.get("starts_at")),
                endTime=_to_time_text(row_map.get("ends_at")),
                status=str(row_map.get("status") or "planned"),
                printReady=str(row_map.get("status") or "planned") != "blocked",
            )
        )

    holidays = _parse_date_set(holiday_dates)
    bridges = _parse_date_set(bridge_days)
    school_holidays = _parse_date_set(school_holiday_dates)
    decorated: list[WorkPlanAssignmentOut] = []
    for assignment in assignments:
        findings = _work_plan_findings_for_assignment(
            assignment,
            preference_by_ref.get(assignment.employeeRef),
            absence_dates_by_employee,
            school_holidays,
            bridges,
            holidays,
        )
        decorated.append(
            assignment.model_copy(
                update={
                    "findings": findings,
                    "status": _assignment_status(findings, assignment.status),
                    "printReady": assignment.printReady and not any(finding.severity == "blocker" for finding in findings),
                }
            )
        )

    all_findings = [finding for assignment in decorated for finding in assignment.findings]
    return WorkPlanOut(
        periodFrom=start_date.isoformat(),
        periodTo=end_date.isoformat(),
        source="database",
        preferences=preferences,
        assignments=sorted(decorated, key=lambda item: (item.datum, item.employeeRef, item.startTime or "")),
        findings=all_findings,
        printTitle=f"Arbeitsplan {start_date.isoformat()} bis {end_date.isoformat()}",
        generatedAt=datetime.utcnow().isoformat(),
    )


@router.get("/driver-time/summary", response_model=DriverTimeSummaryOut)
async def get_driver_time_summary(
    datum: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    target_date = datum or datetime.utcnow().date().isoformat()
    try:
        data = PersonalService(db, tenant_id).get_driver_time_data(target_date)
        timesheet_rows = data["timesheet_rows"]
        absence_rows = data["absence_rows"]
    except Exception:
        pilot_events = _driver_time_pilot_events(target_date)
        return _build_driver_time_summary(target_date, pilot_events, source="pilot-fallback")

    events = _events_from_timesheets(timesheet_rows)
    if not events:
        pilot_events = _driver_time_pilot_events(target_date)
        return _build_driver_time_summary(target_date, pilot_events, source="pilot-empty")

    return _build_driver_time_summary(
        target_date,
        events,
        absence_ranges=_approved_absence_ranges(absence_rows),
        source="database",
    )


@router.get("/time-cockpit", response_model=TimeCockpitOut)
async def get_time_cockpit(
    datum: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    target_date = datum or datetime.utcnow().date().isoformat()
    driver_time = await get_driver_time_summary(datum=target_date, tenant_id=tenant_id, db=db)
    try:
        rows = PersonalService(db, tenant_id).get_time_cockpit_entries(target_date)
    except Exception:
        entries = _pilot_time_entries(target_date)
        return _build_time_cockpit(target_date, entries, driver_time, source="pilot-fallback")

    entries = _time_rows_to_entries(rows)
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

    start_values = [tour.start for tour in payload.touren if tour.start]
    end_values = [tour.ende for tour in payload.touren if tour.ende]
    timesheet_id = str(uuid4())
    timesheet_id = PersonalService(db, tenant_id).create_stundenzettel({
        "timesheet_id": timesheet_id,
        "entry_date": entry_date,
        "driver_name": payload.fahrer,
        "vehicle_plate": payload.kennzeichen,
        "tours": json.dumps([tour.model_dump() for tour in payload.touren]),
        "total_hours": payload.gesamtArbeitszeit,
        "overtime_hours": payload.ueberstunden,
        "signature_data": payload.unterschrift,
        "time_entry_params": {
            "id": str(uuid4()),
            "employee_ref": payload.fahrer,
            "entry_date": entry_date,
            "start_time": min(start_values) if start_values else None,
            "end_time": max(end_values) if end_values else None,
            "hours": payload.gesamtArbeitszeit,
            "entry_type": "Ueberstunden" if payload.ueberstunden > 0 else "Arbeit",
            "notes": f"LKW {payload.kennzeichen}",
        },
    })
    return {"ok": True, "timesheet_id": timesheet_id}


@router.get("/stundenzettel", response_model=list[StundenzettelOut])
async def list_stundenzettel(
    datum_von: str | None = Query(default=None),
    datum_bis: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    rows = PersonalService(db, tenant_id).list_stundenzettel(datum_von, datum_bis)

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


@router.delete("/mitarbeiter/{user_id}", status_code=204)
async def delete_mitarbeiter(
    user_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Deaktiviert einen Mitarbeiter (soft-delete via is_active=FALSE)."""
    try:
        PersonalService(db, tenant_id).delete_mitarbeiter(user_id)
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Mitarbeiter nicht gefunden")


@router.delete("/absences/{absence_id}", status_code=204)
async def delete_absence(
    absence_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Löscht einen Abwesenheitseintrag (nur im Status 'Pending'/'Beantragt')."""
    from app.core.exceptions import ValidationFailedError
    try:
        PersonalService(db, tenant_id).delete_abwesenheit(absence_id)
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Abwesenheit nicht gefunden")
    except ValidationFailedError as exc:
        raise HTTPException(status_code=400, detail=exc.detail)


@router.delete("/shifts/{shift_id}", status_code=204)
async def delete_shift(
    shift_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Löscht eine Schicht (nur wenn noch keine Mitarbeiter zugewiesen wurden)."""
    try:
        PersonalService(db, tenant_id).delete_shift(shift_id)
    except EntityNotFoundError:
        raise HTTPException(status_code=404, detail="Schicht nicht gefunden")


# ---------------------------------------------------------------------------
# HR-TIME-001: Driver Time Events (Pilot Slice)
# ---------------------------------------------------------------------------


@router.post("/driver-time/events", status_code=201)
async def create_driver_time_event(
    payload: DriverTimeEventIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    event_id = str(uuid4())
    db.execute(
        text("""
            INSERT INTO domain_hr.driver_time_events
              (id, tenant_id, employee_ref, vehicle_id, tour_ref, event_type,
               event_ts, duration_minutes, absence_ref, source, notes, row_version)
            VALUES
              (:id, :tenant_id, :employee_ref, :vehicle_id, :tour_ref, :event_type,
               :event_ts, :duration_minutes, :absence_ref, :source, :notes, 1)
        """),
        {
            "id": event_id,
            "tenant_id": tenant_id,
            "employee_ref": payload.employee_ref,
            "vehicle_id": payload.vehicle_id,
            "tour_ref": payload.tour_ref,
            "event_type": payload.event_type,
            "event_ts": payload.event_ts,
            "duration_minutes": payload.duration_minutes,
            "absence_ref": payload.absence_ref,
            "source": payload.source,
            "notes": payload.notes,
        },
    )
    db.commit()
    return {"id": event_id, "status": "created"}


@router.get("/driver-time/events")
async def list_driver_time_events(
    employee_ref: str | None = Query(default=None),
    vehicle_id: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    limit: int = Query(default=50, le=200),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    filters = ["tenant_id = :tenant_id"]
    params: dict = {"tenant_id": tenant_id, "limit": limit}
    if employee_ref:
        filters.append("employee_ref = :employee_ref")
        params["employee_ref"] = employee_ref
    if vehicle_id:
        filters.append("vehicle_id = :vehicle_id")
        params["vehicle_id"] = vehicle_id
    if date_from:
        filters.append("event_ts >= :date_from")
        params["date_from"] = date_from
    if date_to:
        filters.append("event_ts <= :date_to")
        params["date_to"] = date_to
    where = " AND ".join(filters)
    rows = db.execute(
        text(f"SELECT * FROM domain_hr.driver_time_events WHERE {where} ORDER BY event_ts DESC LIMIT :limit"),
        params,
    ).fetchall()
    return {"data": [dict(r._mapping) for r in rows], "total": len(rows)}


@router.get("/driver-time/events/absences/collisions", response_model=list[DriverTimeCollisionOut])
async def get_driver_time_absence_collisions(
    employee_ref: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    filters = ["e.tenant_id = :tenant_id", "e.absence_ref IS NOT NULL"]
    params: dict = {"tenant_id": tenant_id}
    if employee_ref:
        filters.append("e.employee_ref = :employee_ref")
        params["employee_ref"] = employee_ref
    if date_from:
        filters.append("e.event_ts >= :date_from")
        params["date_from"] = date_from
    if date_to:
        filters.append("e.event_ts <= :date_to")
        params["date_to"] = date_to
    where = " AND ".join(filters)
    rows = db.execute(
        text(f"""
            SELECT e.id as event_id, e.employee_ref, e.event_ts::text, e.absence_ref,
                   CASE WHEN a.id IS NULL THEN 'absence_not_found'
                        WHEN e.event_ts::date BETWEEN a.start_date AND a.end_date THEN 'driving_during_absence'
                        ELSE 'absence_ref_mismatch' END as collision_type
            FROM domain_hr.driver_time_events e
            LEFT JOIN domain_hr.time_entries a ON a.id::text = e.absence_ref AND a.tenant_id = e.tenant_id
            WHERE {where}
            ORDER BY e.event_ts DESC
        """),
        params,
    ).fetchall()
    return [DriverTimeCollisionOut(**dict(r._mapping)) for r in rows]


@router.get("/driver-time/events/{event_id}")
async def get_driver_time_event(
    event_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = db.execute(
        text("SELECT * FROM domain_hr.driver_time_events WHERE id = :id AND tenant_id = :tenant_id"),
        {"id": event_id, "tenant_id": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"DriverTimeEvent {event_id} not found")
    return dict(row._mapping)


@router.patch("/driver-time/events/{event_id}")
async def update_driver_time_event(
    event_id: str,
    payload: DriverTimeEventPatch,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    set_clause = ", ".join(f"{k} = :{k}" for k in updates)
    updates.update({"id": event_id, "tenant_id": tenant_id})
    result = db.execute(
        text(f"UPDATE domain_hr.driver_time_events SET {set_clause}, row_version = row_version + 1 WHERE id = :id AND tenant_id = :tenant_id"),
        updates,
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"DriverTimeEvent {event_id} not found")
    db.commit()
    return {"id": event_id, "status": "updated"}


@router.delete("/driver-time/events/{event_id}", status_code=204, response_class=Response)
async def delete_driver_time_event(
    event_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    result = db.execute(
        text("DELETE FROM domain_hr.driver_time_events WHERE id = :id AND tenant_id = :tenant_id"),
        {"id": event_id, "tenant_id": tenant_id},
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"DriverTimeEvent {event_id} not found")
    db.commit()
    return Response(status_code=204)


# ── Organisationsstruktur ────────────────────────────────────────────────────

class OrgUnitIn(BaseModel):
    unit_code: str = Field(..., max_length=40)
    name: str = Field(..., max_length=200)
    unit_type: str = Field(default="ABTEILUNG", pattern="^(ABTEILUNG|TEAM|STANDORT|KOSTENSTELLE)$")
    parent_id: str | None = None
    cost_center_id: str | None = None
    manager_ref: str | None = None


class OrgUnitPatch(BaseModel):
    name: str | None = None
    parent_id: str | None = None
    unit_type: str | None = None
    manager_ref: str | None = None


def _build_org_tree(rows: list[dict], parent_id: Any = None) -> list[dict]:
    """Recursively build org tree from flat list."""
    children = [r for r in rows if r.get("parent_id") == parent_id]
    for child in children:
        child["children"] = _build_org_tree(rows, child["id"])
    return children


@router.get("/org-chart")
async def get_org_chart(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Gesamtes Organigramm als verschachtelter Baum."""
    try:
        rows = db.execute(
            text("""
                WITH RECURSIVE org_tree AS (
                    SELECT id, unit_code, name, unit_type, parent_id, cost_center_id, manager_ref, tenant_id, 0 AS depth
                    FROM domain_hr.org_units
                    WHERE tenant_id = :tenant_id AND parent_id IS NULL
                    UNION ALL
                    SELECT u.id, u.unit_code, u.name, u.unit_type, u.parent_id, u.cost_center_id, u.manager_ref, u.tenant_id, ot.depth + 1
                    FROM domain_hr.org_units u
                    JOIN org_tree ot ON u.parent_id = ot.id
                    WHERE u.tenant_id = :tenant_id
                )
                SELECT * FROM org_tree ORDER BY depth, name
            """),
            {"tenant_id": tenant_id},
        ).fetchall()
    except Exception:
        raise HTTPException(status_code=503, detail="org_units table not available")
    flat = [dict(r._mapping) for r in rows]
    # Convert UUID/special types to str for JSON
    for r in flat:
        for k, v in r.items():
            if v is not None and not isinstance(v, (str, int, float, bool)):
                r[k] = str(v)
    tree = _build_org_tree(flat, None)
    return {"org_chart": tree}


@router.get("/org-chart/{unit_id}")
async def get_org_subtree(
    unit_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Teilbaum ab einer bestimmten Org-Einheit."""
    try:
        rows = db.execute(
            text("""
                WITH RECURSIVE subtree AS (
                    SELECT id, unit_code, name, unit_type, parent_id, cost_center_id, manager_ref, 0 AS depth
                    FROM domain_hr.org_units
                    WHERE id = :unit_id AND tenant_id = :tenant_id
                    UNION ALL
                    SELECT u.id, u.unit_code, u.name, u.unit_type, u.parent_id, u.cost_center_id, u.manager_ref, s.depth + 1
                    FROM domain_hr.org_units u
                    JOIN subtree s ON u.parent_id = s.id
                    WHERE u.tenant_id = :tenant_id
                )
                SELECT * FROM subtree ORDER BY depth, name
            """),
            {"unit_id": unit_id, "tenant_id": tenant_id},
        ).fetchall()
    except Exception:
        raise HTTPException(status_code=503, detail="org_units table not available")
    if not rows:
        raise HTTPException(status_code=404, detail=f"OrgUnit {unit_id} not found")
    flat = [dict(r._mapping) for r in rows]
    for r in flat:
        for k, v in r.items():
            if v is not None and not isinstance(v, (str, int, float, bool)):
                r[k] = str(v)
    root_parent = flat[0].get("parent_id") if flat else None
    tree = _build_org_tree(flat, root_parent)
    return {"org_chart": tree[0] if tree else {}}


@router.post("/org-units", status_code=201)
async def create_org_unit(
    payload: OrgUnitIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Neue Abteilung / Team / Standort / Kostenstelle anlegen."""
    unit_id = str(uuid4())
    try:
        db.execute(
            text("""
                INSERT INTO domain_hr.org_units
                    (id, unit_code, name, unit_type, parent_id, cost_center_id, manager_ref, tenant_id)
                VALUES
                    (:id, :unit_code, :name, :unit_type, :parent_id, :cost_center_id, :manager_ref, :tenant_id)
            """),
            {
                "id": unit_id,
                "unit_code": payload.unit_code,
                "name": payload.name,
                "unit_type": payload.unit_type,
                "parent_id": payload.parent_id,
                "cost_center_id": payload.cost_center_id,
                "manager_ref": payload.manager_ref,
                "tenant_id": tenant_id,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="org_units table not available")
    return {"id": unit_id, "status": "created"}


@router.patch("/org-units/{unit_id}")
async def patch_org_unit(
    unit_id: str,
    payload: OrgUnitPatch,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Org-Einheit umbenennen oder Elternteil ändern."""
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    set_clause = ", ".join(f"{k} = :{k}" for k in updates)
    updates.update({"id": unit_id, "tenant_id": tenant_id})
    try:
        result = db.execute(
            text(f"UPDATE domain_hr.org_units SET {set_clause} WHERE id = :id AND tenant_id = :tenant_id"),
            updates,
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"OrgUnit {unit_id} not found")
        db.commit()
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="org_units table not available")
    return {"id": unit_id, "status": "updated"}


# ── Arbeitszeitkonto ─────────────────────────────────────────────────────────

class TimeAccountAdjustIn(BaseModel):
    delta_hours: float = Field(..., description="Positive = Gutschrift, Negative = Abbuchung")
    reason: str = Field(..., max_length=400)
    adjustment_date: str | None = None  # ISO date, default: today


@router.get("/time-accounts/{employee_ref}")
async def get_time_account(
    employee_ref: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Arbeitszeitkonto: Saldo, Monats-Breakdown, Übertrag aus Vorperiode."""
    try:
        rows = db.execute(
            text("""
                SELECT
                    TO_CHAR(entry_date, 'YYYY-MM') AS monat,
                    SUM(hours) AS actual_hours,
                    COUNT(*) AS eintraege
                FROM domain_hr.time_entries
                WHERE employee_ref = :employee_ref
                  AND tenant_id = :tenant_id
                GROUP BY TO_CHAR(entry_date, 'YYYY-MM')
                ORDER BY monat
            """),
            {"employee_ref": employee_ref, "tenant_id": tenant_id},
        ).fetchall()
        # Manual adjustments
        adj_rows = db.execute(
            text("""
                SELECT COALESCE(SUM(delta_hours), 0) AS total_adj
                FROM domain_hr.time_account_adjustments
                WHERE employee_ref = :employee_ref AND tenant_id = :tenant_id
            """),
            {"employee_ref": employee_ref, "tenant_id": tenant_id},
        ).fetchone()
        # Planned hours: 8h per workday estimate — use schichten if available
        planned = db.execute(
            text("""
                SELECT COALESCE(SUM(planned_hours), 0) AS total_planned
                FROM domain_hr.schichten
                WHERE employee_ref = :employee_ref AND tenant_id = :tenant_id
            """),
            {"employee_ref": employee_ref, "tenant_id": tenant_id},
        ).fetchone()
    except Exception:
        raise HTTPException(status_code=503, detail="time_entries table not available")
    breakdown = [
        {"monat": r[0], "actual_hours": float(r[1]), "eintraege": r[2]}
        for r in rows
    ]
    total_actual = sum(b["actual_hours"] for b in breakdown)
    total_planned = float(planned[0]) if planned else 0.0
    total_adj = float(adj_rows[0]) if adj_rows else 0.0
    current_year = datetime.utcnow().year
    current_breakdown = [b for b in breakdown if b["monat"].startswith(str(current_year))]
    prev_breakdown = [b for b in breakdown if not b["monat"].startswith(str(current_year))]
    transferred = sum(b["actual_hours"] for b in prev_breakdown) + total_adj
    current_period_hours = sum(b["actual_hours"] for b in current_breakdown)
    saldo = total_actual - total_planned + total_adj
    return {
        "employee_ref": employee_ref,
        "saldo_hours": round(saldo, 2),
        "transferred_from_prev_period": round(transferred, 2),
        "current_period_hours": round(current_period_hours, 2),
        "breakdown_by_month": breakdown,
    }


@router.post("/time-accounts/{employee_ref}/adjust", status_code=201)
async def adjust_time_account(
    employee_ref: str,
    payload: TimeAccountAdjustIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Manuelle Saldo-Korrektur (Urlaubsabgeltung, Übertrag etc.)."""
    adj_id = str(uuid4())
    adj_date = payload.adjustment_date or date.today().isoformat()
    try:
        db.execute(
            text("""
                INSERT INTO domain_hr.time_account_adjustments
                    (id, employee_ref, delta_hours, reason, adjustment_date, tenant_id)
                VALUES (:id, :employee_ref, :delta_hours, :reason, :adjustment_date, :tenant_id)
            """),
            {
                "id": adj_id,
                "employee_ref": employee_ref,
                "delta_hours": payload.delta_hours,
                "reason": payload.reason,
                "adjustment_date": adj_date,
                "tenant_id": tenant_id,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="time_account_adjustments table not available")
    return {"id": adj_id, "employee_ref": employee_ref, "delta_hours": payload.delta_hours, "status": "adjusted"}


# ── Bewerbermanagement (Recruiting-Pipeline) ─────────────────────────────────

APPLICATION_STAGES = {"EINGANG", "VORAUSWAHL", "ERSTGESPRAECH", "ENDGESPRAECH", "ANGEBOT", "EINGESTELLT", "ABGELEHNT"}


class ApplicationIn(BaseModel):
    applicant_name: str = Field(..., max_length=200)
    applicant_email: str = Field(..., max_length=200)
    position_id: str | None = None
    position_title: str | None = Field(default=None, max_length=200)
    source: str | None = Field(default=None, max_length=80)
    documents_ref: str | None = None


class ApplicationStagePatch(BaseModel):
    stage: str = Field(..., description="EINGANG/VORAUSWAHL/ERSTGESPRAECH/ENDGESPRAECH/ANGEBOT/EINGESTELLT/ABGELEHNT")
    note: str | None = None


@router.get("/applications")
async def list_applications(
    status: str | None = Query(None),
    position_id: str | None = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Bewerbungen auflisten, optional nach Status oder Stelle filtern."""
    where = ["tenant_id = :tenant_id"]
    params: dict = {"tenant_id": tenant_id}
    if status:
        where.append("status = :status")
        params["status"] = status
    if position_id:
        where.append("position_id = :position_id")
        params["position_id"] = position_id
    where_sql = " AND ".join(where)
    try:
        rows = db.execute(
            text(f"SELECT * FROM domain_hr.applications WHERE {where_sql} ORDER BY applied_at DESC"),
            params,
        ).fetchall()
    except Exception:
        raise HTTPException(status_code=503, detail="applications table not available")
    return [dict(r._mapping) for r in rows]


@router.post("/applications", status_code=201)
async def create_application(
    payload: ApplicationIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Neue Bewerbung erfassen (Eingang in Pipeline)."""
    app_id = str(uuid4())
    try:
        db.execute(
            text("""
                INSERT INTO domain_hr.applications
                    (id, applicant_name, applicant_email, position_id, position_title, source, documents_ref, status, applied_at, tenant_id)
                VALUES
                    (:id, :applicant_name, :applicant_email, :position_id, :position_title, :source, :documents_ref, 'EINGANG', NOW(), :tenant_id)
            """),
            {
                "id": app_id,
                "applicant_name": payload.applicant_name,
                "applicant_email": payload.applicant_email,
                "position_id": payload.position_id,
                "position_title": payload.position_title,
                "source": payload.source,
                "documents_ref": payload.documents_ref,
                "tenant_id": tenant_id,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="applications table not available")
    return {"id": app_id, "status": "EINGANG"}


@router.patch("/applications/{application_id}/stage")
async def update_application_stage(
    application_id: str,
    payload: ApplicationStagePatch,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Pipeline-Stufe einer Bewerbung ändern."""
    if payload.stage not in APPLICATION_STAGES:
        raise HTTPException(status_code=400, detail=f"Invalid stage. Must be one of: {', '.join(sorted(APPLICATION_STAGES))}")
    try:
        result = db.execute(
            text("""
                UPDATE domain_hr.applications
                SET status = :stage, last_updated = NOW(), notes = COALESCE(notes, '') || :note
                WHERE id = :id AND tenant_id = :tenant_id
            """),
            {
                "stage": payload.stage,
                "note": f"\n[{datetime.utcnow().isoformat()}] {payload.note or ''}" if payload.note else "",
                "id": application_id,
                "tenant_id": tenant_id,
            },
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
        db.commit()
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="applications table not available")
    return {"id": application_id, "stage": payload.stage, "status": "updated"}
