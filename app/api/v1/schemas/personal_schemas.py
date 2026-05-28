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
