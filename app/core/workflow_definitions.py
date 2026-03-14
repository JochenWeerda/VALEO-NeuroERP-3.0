"""
Gap 011: Versionierte Workflow-Definitionen mit Migrations-Registry.
Ziel: 0 ungeplante Workflow-Brüche bei Releases.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional
from pydantic import BaseModel, Field

from app.services.workflow_guards import (
    guard_total_positive,
    guard_price_not_below_cost,
    guard_has_approval_role,
    guard_has_submit_role,
)

TransitionGuard = Callable[[dict], tuple[bool, str]]


@dataclass
class TransitionDef:
    name: str
    src: str
    dst: str
    guard: Optional[TransitionGuard] = None


@dataclass
class WorkflowDef:
    domain: str
    version: str
    states: List[str]
    transitions: List[TransitionDef]
    description: str = ""


# State-Migration: (from_version, to_version) -> (old_state -> new_state)
MigrationFn = Callable[[str], str]
MIGRATIONS: Dict[tuple[str, str], MigrationFn] = {}


def register_migration(domain: str, from_ver: str, to_ver: str, fn: MigrationFn) -> None:
    """Registriert eine Migrationsfunktion für Workflow-Upgrades."""
    MIGRATIONS[(domain, f"{from_ver}->{to_ver}")] = fn


def migrate_state(domain: str, from_ver: str, to_ver: str, state: str) -> str:
    """
    Migriert einen State von alter zu neuer Workflow-Version.
    Falls keine Migration registriert: 1:1 übernehmen (state unverändert).
    """
    key = (domain, f"{from_ver}->{to_ver}")
    fn = MIGRATIONS.get(key)
    if fn:
        return fn(state)
    return state


# Default-Definitionen (Version 1) – kompatibel mit bisherigem Verhalten
DEFAULT_DEFINITIONS: List[WorkflowDef] = [
    WorkflowDef(
        domain="sales",
        version="1",
        states=["draft", "pending", "approved", "posted", "rejected"],
        transitions=[
            TransitionDef("submit", "draft", "pending", guard_has_submit_role),
            TransitionDef("approve", "pending", "approved", guard_price_not_below_cost),
            TransitionDef("reject", "pending", "rejected", guard_has_approval_role),
            TransitionDef("post", "approved", "posted", guard_total_positive),
        ],
        description="Sales Order Workflow v1",
    ),
    WorkflowDef(
        domain="purchase",
        version="1",
        states=["draft", "pending", "approved", "posted", "rejected"],
        transitions=[
            TransitionDef("submit", "draft", "pending", guard_has_submit_role),
            TransitionDef("approve", "pending", "approved", guard_has_approval_role),
            TransitionDef("reject", "pending", "rejected", guard_has_approval_role),
            TransitionDef("post", "approved", "posted", guard_total_positive),
        ],
        description="Purchase Order Workflow v1",
    ),
]

_REGISTRY: Dict[tuple[str, str], WorkflowDef] = {}


def _build_registry() -> Dict[tuple[str, str], WorkflowDef]:
    if not _REGISTRY:
        for wf in DEFAULT_DEFINITIONS:
            _REGISTRY[(wf.domain, wf.version)] = wf
    return _REGISTRY


def get_workflow_def(domain: str, version: str = "1") -> Optional[WorkflowDef]:
    """Holt Workflow-Definition für Domain und Version."""
    reg = _build_registry()
    return reg.get((domain, version))


def get_latest_version(domain: str) -> str:
    """Holt die neueste Version für eine Domain."""
    reg = _build_registry()
    versions = [v for (d, v) in reg if d == domain]
    return max(versions) if versions else "1"


def register_definition(wf: WorkflowDef) -> None:
    """Registriert eine zusätzliche Workflow-Definition (z.B. aus DB/Config)."""
    _build_registry()
    _REGISTRY[(wf.domain, wf.version)] = wf


class WorkflowStepSla(BaseModel):
    timeout_hours: int | None = Field(default=None, ge=0)
    escalation_roles: list[str] = Field(default_factory=list)


class WorkflowDefinition(BaseModel):
    process_key: str | None = Field(default=None, min_length=1)
    version: int = Field(default=1, ge=1)
    origin: str = Field(default="default", min_length=1)
    tenant_id: str | None = None
    status: str = "active"
    steps: list[str] = Field(default_factory=list)
    required_roles: dict[str, list[str]] = Field(default_factory=dict)
    step_sla: dict[str, WorkflowStepSla] = Field(default_factory=dict)
    description: str | None = None


class WorkflowVariantsPayload(BaseModel):
    variants: dict[str, WorkflowDefinition] = Field(default_factory=dict)


def merge_workflow_variants(
    defaults: dict[str, dict],
    custom: object,
    *,
    tenant_id: str | None = None,
) -> dict[str, WorkflowDefinition]:
    merged: dict[str, WorkflowDefinition] = {}

    for process_key, definition in defaults.items():
        merged[process_key] = WorkflowDefinition.model_validate(
            {
                **definition,
                "process_key": process_key,
                "origin": "default",
                "tenant_id": tenant_id,
            }
        )

    if isinstance(custom, dict):
        for process_key, definition in custom.items():
            if not isinstance(definition, dict):
                continue
            base = merged.get(process_key)
            merged[process_key] = WorkflowDefinition.model_validate(
                {
                    **(base.model_dump() if base else {}),
                    **definition,
                    "process_key": process_key,
                    "origin": definition.get("origin")
                    or ("tenant-override" if tenant_id else "custom"),
                    "tenant_id": tenant_id,
                }
            )

    return merged
