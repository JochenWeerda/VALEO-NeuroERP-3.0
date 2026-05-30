"""Read-only Admin Suite production-readiness aggregation."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.integration_bootstrap import build_integration_bootstrap_summary


router = APIRouter(prefix="/admin-suite", tags=["admin-suite", "readiness"])

ReadinessStatus = Literal["ready", "warning", "blocked", "unchecked"]


class ReadinessEvidence(BaseModel):
    key: str
    label: str
    status: ReadinessStatus
    source: str
    evidence: str
    details: list[str] = Field(default_factory=list)
    checked_at: datetime


class AdminSuiteReadinessOut(BaseModel):
    status: ReadinessStatus
    score: int = Field(ge=0, le=100)
    ready_count: int
    warning_count: int
    blocked_count: int
    unchecked_count: int
    evaluated_count: int
    checked_at: datetime
    evidence: list[ReadinessEvidence]


def _evidence(
    *,
    key: str,
    label: str,
    status: ReadinessStatus,
    source: str,
    evidence: str,
    checked_at: datetime,
    details: list[str] | None = None,
) -> ReadinessEvidence:
    return ReadinessEvidence(
        key=key,
        label=label,
        status=status,
        source=source,
        evidence=evidence,
        details=details or [],
        checked_at=checked_at,
    )


def _integration_evidence(summary: dict[str, Any], checked_at: datetime) -> ReadinessEvidence:
    blockers = [str(item) for item in summary.get("required_blockers", [])]
    partial_count = int(summary.get("partial_count", 0))
    disabled_count = int(summary.get("disabled_count", 0))
    ready_count = int(summary.get("ready_count", 0))
    status: ReadinessStatus = "blocked" if blockers else "warning"
    details = [
        f"Konfiguriert: {ready_count}",
        f"Teilweise konfiguriert: {partial_count}",
        f"Deaktiviert: {disabled_count}",
    ]
    if blockers:
        details.append(f"Pflichtblocker: {', '.join(blockers)}")
    details.append("Live-Probes wurden durch diesen Readiness-Aufruf nicht ausgefuehrt.")
    return _evidence(
        key="connectors",
        label="Schnittstellen",
        status=status,
        source="app.services.integration_bootstrap",
        evidence="Konfigurationspruefung vorhanden; produktive Live-Evidenz steht noch aus.",
        checked_at=checked_at,
        details=details,
    )


def build_admin_suite_readiness() -> AdminSuiteReadinessOut:
    checked_at = datetime.now(timezone.utc)
    items = [
        _evidence(
            key="setup",
            label="Ersteinrichtung",
            status="unchecked",
            source="/admin/setup",
            evidence="Einzelne Setup-Seiten existieren; ein persistierter Abschlussnachweis fehlt.",
            checked_at=checked_at,
        ),
        _evidence(
            key="migration",
            label="Datenmigration",
            status="warning",
            source="scripts/import_l3.py",
            evidence="L3 Dry Run und Staging sind vorhanden; fachliche Abnahme und Reconciliation fehlen im Cockpit.",
            checked_at=checked_at,
        ),
        _evidence(
            key="security",
            label="Rollen und Rechte",
            status="warning",
            source="/api/v1/admin/roles",
            evidence="Benutzer- und Rollenverwaltung sind vorhanden; zentrale Rechte-Simulation und SoD-Sicht fehlen.",
            checked_at=checked_at,
        ),
        _integration_evidence(build_integration_bootstrap_summary(), checked_at),
        _evidence(
            key="devices",
            label="Hardware",
            status="warning",
            source="/api/v1/admin/devices",
            evidence="Device-Verwaltung ist vorhanden; Standort-UAT, Heartbeats und reale Testaktionen sind nicht aggregiert.",
            checked_at=checked_at,
        ),
        _evidence(
            key="compliance",
            label="Compliance",
            status="unchecked",
            source="/admin/compliance",
            evidence="Fachliche Compliance-Sichten existieren; produktive externe Abnahmen werden noch nicht aggregiert.",
            checked_at=checked_at,
        ),
        _evidence(
            key="backup_restore",
            label="Backup und Restore",
            status="unchecked",
            source="k8s/helm/valeo-erp/templates/restore-test-cronjob.yaml",
            evidence="Restore-Test-Job ist deploybar; letzter produktiver Restore-Drill ist nicht als Evidenz angebunden.",
            checked_at=checked_at,
        ),
        _evidence(
            key="system_status",
            label="Systemstatus",
            status="unchecked",
            source="/api/v1/health/ready",
            evidence="Technische Readiness-Probe existiert; sie wurde durch diesen lesenden Aggregator nicht ausgefuehrt.",
            checked_at=checked_at,
        ),
    ]
    ready_count = sum(item.status == "ready" for item in items)
    warning_count = sum(item.status == "warning" for item in items)
    blocked_count = sum(item.status == "blocked" for item in items)
    unchecked_count = sum(item.status == "unchecked" for item in items)
    evaluated_count = ready_count + warning_count + blocked_count
    score = round(100 * ready_count / evaluated_count) if evaluated_count else 0
    overall: ReadinessStatus
    if blocked_count:
        overall = "blocked"
    elif warning_count or unchecked_count:
        overall = "warning"
    else:
        overall = "ready"
    return AdminSuiteReadinessOut(
        status=overall,
        score=score,
        ready_count=ready_count,
        warning_count=warning_count,
        blocked_count=blocked_count,
        unchecked_count=unchecked_count,
        evaluated_count=evaluated_count,
        checked_at=checked_at,
        evidence=items,
    )


@router.get("/readiness", response_model=AdminSuiteReadinessOut, summary="Admin Suite readiness abrufen")
async def get_admin_suite_readiness() -> AdminSuiteReadinessOut:
    """Liefert konservative Go-Live-Evidenz ohne externe Live-Probes."""
    return build_admin_suite_readiness()
