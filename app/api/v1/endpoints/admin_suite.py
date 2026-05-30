"""Read-only Admin Suite production-readiness aggregation."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any, Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.integration_bootstrap import build_integration_bootstrap_summary


router = APIRouter(prefix="/admin-suite", tags=["admin-suite", "readiness"])

ReadinessStatus = Literal["ready", "warning", "blocked", "unchecked"]
SetupStepStatus = Literal["unchecked", "in_progress", "warning", "blocked", "completed"]
MigrationBatchStatus = Literal["dry_run", "staged", "reconciliation_pending", "approved", "blocked"]

SETUP_STEPS = (
    ("company", "Firma", "/setup/firma"),
    ("locations", "Standorte", "/stammdaten/betriebsstaetten"),
    ("fiscal_year", "Geschaeftsjahr", "/fibu/geschaeftsjahre"),
    ("chart_of_accounts", "Kontenrahmen", "/fibu/kontenplan"),
    ("taxes", "Steuern", "/fibu/steuerkennzeichen"),
    ("number_ranges", "Nummernkreise", "/admin/nummernkreise"),
    ("users", "Benutzer", "/admin/benutzer"),
    ("roles", "Rollen", "/admin/rollen-verwaltung"),
    ("devices", "Geraete", None),
    ("connectors", "Schnittstellen", "/admin/control-center/superglue"),
    ("migration", "Import", None),
    ("go_live_test", "Abschlusspruefung", "/admin-suite"),
)

MIGRATION_PROFILES = (
    {
        "key": "l3",
        "label": "L3 / zvoove Handel",
        "status": "available",
        "adapter": "scripts/import_l3.py",
        "notes": "Bestehender Dry-Run-, Staging- und Run-Tracking-Pfad.",
    },
    {
        "key": "csv",
        "label": "CSV / Excel",
        "status": "available",
        "adapter": "admin-suite-control-plane",
        "notes": "Profilierung und Mapping vor spaeterem Import erforderlich.",
    },
    {
        "key": "amic",
        "label": "AMIC / AMIC A.eins",
        "status": "blocked",
        "adapter": None,
        "notes": "Produktives Quellenprofil und Feldkatalog muessen verifiziert werden.",
    },
    {
        "key": "rest_api",
        "label": "REST API",
        "status": "planned",
        "adapter": None,
        "notes": "Folgeprofil nach CSV und AMIC.",
    },
)
RECONCILIATION_KEYS = ("record_counts", "balances", "open_items", "inventory")


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


class SetupStepOut(BaseModel):
    key: str
    label: str
    status: SetupStepStatus
    target_path: str | None = None
    evidence: str | None = None
    responsible: str | None = None
    updated_at: datetime | None = None


class SetupSessionOut(BaseModel):
    tenant_id: str
    status: SetupStepStatus
    completed_count: int
    total_count: int
    updated_at: datetime | None = None
    steps: list[SetupStepOut]


class SetupStepUpdate(BaseModel):
    status: SetupStepStatus
    evidence: str | None = Field(default=None, max_length=1000)
    responsible: str | None = Field(default=None, max_length=120)


class MigrationProfileOut(BaseModel):
    key: str
    label: str
    status: Literal["available", "blocked", "planned"]
    adapter: str | None = None
    notes: str


class MigrationBatchCreate(BaseModel):
    source_profile: str
    source_ref: str = Field(min_length=1, max_length=255)
    source_hash: str = Field(min_length=8, max_length=128)
    mapping_version: str = Field(min_length=1, max_length=80)
    dry_run: Literal[True] = True


class MigrationReconciliationUpdate(BaseModel):
    checks: dict[str, bool]


class MigrationBatchOut(BaseModel):
    id: str
    tenant_id: str
    source_profile: str
    source_ref: str
    source_hash: str
    mapping_version: str
    dry_run: bool
    status: MigrationBatchStatus
    reconciliation: dict[str, bool]
    created_at: datetime
    updated_at: datetime


class MigrationCockpitOut(BaseModel):
    profiles: list[MigrationProfileOut]
    batches: list[MigrationBatchOut]


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


def _load_tenant_settings(db: Session, tenant_id: str) -> dict[str, Any]:
    row = db.execute(
        text("SELECT settings FROM domain_shared.tenants WHERE id = :tenant_id"),
        {"tenant_id": tenant_id},
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"Tenant not found: {tenant_id}")
    raw = row[0]
    if not raw:
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _save_tenant_settings(db: Session, tenant_id: str, settings: dict[str, Any]) -> None:
    db.execute(
        text("UPDATE domain_shared.tenants SET settings = :settings, updated_at = NOW() WHERE id = :tenant_id"),
        {"tenant_id": tenant_id, "settings": json.dumps(settings)},
    )
    db.commit()


def _build_setup_session(tenant_id: str, payload: dict[str, Any] | None) -> SetupSessionOut:
    stored = payload if isinstance(payload, dict) else {}
    stored_steps = stored.get("steps") if isinstance(stored.get("steps"), dict) else {}
    steps: list[SetupStepOut] = []
    for key, label, target_path in SETUP_STEPS:
        step = stored_steps.get(key) if isinstance(stored_steps.get(key), dict) else {}
        steps.append(
            SetupStepOut(
                key=key,
                label=label,
                status=step.get("status", "unchecked"),
                target_path=target_path,
                evidence=step.get("evidence"),
                responsible=step.get("responsible"),
                updated_at=step.get("updated_at"),
            )
        )
    completed_count = sum(step.status == "completed" for step in steps)
    if any(step.status == "blocked" for step in steps):
        status: SetupStepStatus = "blocked"
    elif completed_count == len(steps):
        status = "completed"
    elif any(step.status in {"in_progress", "warning", "completed"} for step in steps):
        status = "in_progress"
    else:
        status = "unchecked"
    return SetupSessionOut(
        tenant_id=tenant_id,
        status=status,
        completed_count=completed_count,
        total_count=len(steps),
        updated_at=stored.get("updated_at"),
        steps=steps,
    )


def _migration_store(settings: dict[str, Any]) -> dict[str, Any]:
    store = settings.get("admin_suite_migration")
    if not isinstance(store, dict):
        store = {}
    batches = store.get("batches")
    if not isinstance(batches, list):
        batches = []
    store["batches"] = batches
    return store


def _migration_cockpit(tenant_id: str, store: dict[str, Any]) -> MigrationCockpitOut:
    return MigrationCockpitOut(
        profiles=[MigrationProfileOut(**profile) for profile in MIGRATION_PROFILES],
        batches=[MigrationBatchOut(**batch) for batch in store.get("batches", [])],
    )


def _find_batch(store: dict[str, Any], batch_id: str) -> dict[str, Any]:
    batch = next((item for item in store["batches"] if item.get("id") == batch_id), None)
    if not isinstance(batch, dict):
        raise HTTPException(status_code=404, detail=f"Migration batch not found: {batch_id}")
    return batch


@router.get("/readiness", response_model=AdminSuiteReadinessOut, summary="Admin Suite readiness abrufen")
async def get_admin_suite_readiness() -> AdminSuiteReadinessOut:
    """Liefert konservative Go-Live-Evidenz ohne externe Live-Probes."""
    return build_admin_suite_readiness()


@router.get("/setup", response_model=SetupSessionOut, summary="Admin Suite setup session abrufen")
async def get_setup_session(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> SetupSessionOut:
    """Liefert den wiederaufnehmbaren Setup-Fortschritt eines Tenants."""
    settings = _load_tenant_settings(db, tenant_id)
    return _build_setup_session(tenant_id, settings.get("admin_suite_setup"))


@router.patch("/setup/steps/{step_key}", response_model=SetupSessionOut, summary="Admin Suite setup step aktualisieren")
async def update_setup_step(
    step_key: str,
    payload: SetupStepUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> SetupSessionOut:
    """Aktualisiert einen Setup-Schritt nur nach expliziter Nutzeraktion."""
    allowed_steps = {key for key, _, _ in SETUP_STEPS}
    if step_key not in allowed_steps:
        raise HTTPException(status_code=404, detail=f"Unknown setup step: {step_key}")
    settings = _load_tenant_settings(db, tenant_id)
    setup = settings.get("admin_suite_setup")
    if not isinstance(setup, dict):
        setup = {}
    steps = setup.get("steps")
    if not isinstance(steps, dict):
        steps = {}
    checked_at = datetime.now(timezone.utc).isoformat()
    steps[step_key] = {
        "status": payload.status,
        "evidence": payload.evidence,
        "responsible": payload.responsible,
        "updated_at": checked_at,
    }
    setup["steps"] = steps
    setup["updated_at"] = checked_at
    settings["admin_suite_setup"] = setup
    _save_tenant_settings(db, tenant_id, settings)
    return _build_setup_session(tenant_id, setup)


@router.get("/migration", response_model=MigrationCockpitOut, summary="Migration Cockpit abrufen")
async def get_migration_cockpit(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> MigrationCockpitOut:
    settings = _load_tenant_settings(db, tenant_id)
    return _migration_cockpit(tenant_id, _migration_store(settings))


@router.post("/migration/batches", response_model=MigrationBatchOut, status_code=201, summary="Migration Dry Run Batch anlegen")
async def create_migration_batch(
    payload: MigrationBatchCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> MigrationBatchOut:
    profiles = {profile["key"]: profile for profile in MIGRATION_PROFILES}
    profile = profiles.get(payload.source_profile)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Unknown source profile: {payload.source_profile}")
    if profile["status"] != "available":
        raise HTTPException(status_code=409, detail=f"Source profile is not available: {payload.source_profile}")
    settings = _load_tenant_settings(db, tenant_id)
    store = _migration_store(settings)
    checked_at = datetime.now(timezone.utc).isoformat()
    batch = {
        "id": str(uuid4()),
        "tenant_id": tenant_id,
        "source_profile": payload.source_profile,
        "source_ref": payload.source_ref,
        "source_hash": payload.source_hash,
        "mapping_version": payload.mapping_version,
        "dry_run": True,
        "status": "dry_run",
        "reconciliation": {key: False for key in RECONCILIATION_KEYS},
        "created_at": checked_at,
        "updated_at": checked_at,
    }
    store["batches"].append(batch)
    settings["admin_suite_migration"] = store
    _save_tenant_settings(db, tenant_id, settings)
    return MigrationBatchOut(**batch)


@router.patch("/migration/batches/{batch_id}/reconciliation", response_model=MigrationBatchOut, summary="Migration Reconciliation aktualisieren")
async def update_migration_reconciliation(
    batch_id: str,
    payload: MigrationReconciliationUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> MigrationBatchOut:
    unknown = sorted(set(payload.checks) - set(RECONCILIATION_KEYS))
    if unknown:
        raise HTTPException(status_code=422, detail=f"Unknown reconciliation checks: {', '.join(unknown)}")
    settings = _load_tenant_settings(db, tenant_id)
    store = _migration_store(settings)
    batch = _find_batch(store, batch_id)
    reconciliation = dict(batch.get("reconciliation") or {})
    reconciliation.update(payload.checks)
    batch["reconciliation"] = reconciliation
    batch["status"] = "staged" if all(reconciliation.get(key) for key in RECONCILIATION_KEYS) else "reconciliation_pending"
    batch["updated_at"] = datetime.now(timezone.utc).isoformat()
    settings["admin_suite_migration"] = store
    _save_tenant_settings(db, tenant_id, settings)
    return MigrationBatchOut(**batch)


@router.post("/migration/batches/{batch_id}/approve", response_model=MigrationBatchOut, summary="Migration Batch freigeben")
async def approve_migration_batch(
    batch_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> MigrationBatchOut:
    settings = _load_tenant_settings(db, tenant_id)
    store = _migration_store(settings)
    batch = _find_batch(store, batch_id)
    if not batch.get("dry_run"):
        raise HTTPException(status_code=409, detail="Batch without dry run cannot be approved")
    reconciliation = batch.get("reconciliation") or {}
    missing = [key for key in RECONCILIATION_KEYS if not reconciliation.get(key)]
    if missing:
        raise HTTPException(status_code=409, detail=f"Reconciliation incomplete: {', '.join(missing)}")
    batch["status"] = "approved"
    batch["updated_at"] = datetime.now(timezone.utc).isoformat()
    settings["admin_suite_migration"] = store
    _save_tenant_settings(db, tenant_id, settings)
    return MigrationBatchOut(**batch)
