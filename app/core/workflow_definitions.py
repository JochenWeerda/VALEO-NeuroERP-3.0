"""
Gap 011: Versionierte Workflow-Definitionen und Migrations-Registry.
Ziel: 0 ungeplante Workflow-Brüche bei Releases.

Enthält außerdem merge_workflow_variants für Prozess-Varianten (process_config).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from app.services.workflow_guards import (
    guard_has_approval_role,
    guard_has_submit_role,
    guard_price_not_below_cost,
    guard_total_positive,
)

TransitionGuard = Callable[[dict], tuple[bool, str]]


@dataclass
class WorkflowDefinition:
    """Tenant-spezifische oder globale Workflow-Definition (Process-Kernel-Kontrakt)."""

    process_key: str
    version: int
    status: str = "active"
    origin: str = "default"
    tenant_id: Optional[str] = None
    steps: List[str] = None
    required_roles: Dict[str, List[str]] = None
    description: str = ""

    def __post_init__(self) -> None:
        if self.steps is None:
            self.steps = []
        if self.required_roles is None:
            self.required_roles = {}


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


# Registry: (domain, version) -> WorkflowDef
_REGISTRY: Dict[tuple[str, str], WorkflowDef] = {}

# Migrationen: (domain, from_version, to_version) -> Callable[[str], str]
_MIGRATIONS: Dict[tuple[str, str, str], Callable[[str], str]] = {}


def _register_sales_v1() -> None:
    _REGISTRY[("sales", "1")] = WorkflowDef(
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
    )


def _register_purchase_v1() -> None:
    _REGISTRY[("purchase", "1")] = WorkflowDef(
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
    )


def _bootstrap() -> None:
    if not _REGISTRY:
        _register_sales_v1()
        _register_purchase_v1()


def get_workflow_def(domain: str, version: str = "1") -> Optional[WorkflowDef]:
    """Workflow-Definition für Domain und Version abrufen."""
    _bootstrap()
    return _REGISTRY.get((domain, version))


def get_latest_version(domain: str) -> str:
    """Aktuelle Version für eine Domain (für neue Instanzen)."""
    _bootstrap()
    versions = [v for (d, v) in _REGISTRY if d == domain]
    return max(versions) if versions else "1"


def migrate_state(
    domain: str, from_version: str, to_version: str, current_state: str
) -> str:
    """
    Migriert einen State von alter auf neue Workflow-Version.
    Bei unbekannter Migration: State unverändert, wenn in neuer Def vorhanden.
    """
    _bootstrap()
    if from_version == to_version:
        return current_state
    key = (domain, from_version, to_version)
    fn = _MIGRATIONS.get(key)
    if fn:
        return fn(current_state)
    new_def = get_workflow_def(domain, to_version)
    if new_def and current_state in new_def.states:
        return current_state
    return new_def.states[0] if new_def and new_def.states else current_state


def register_definition(defn: WorkflowDef) -> None:
    """Registriert eine Workflow-Definition (Tests/Erweiterungen)."""
    _REGISTRY[(defn.domain, defn.version)] = defn


def register_migration(
    domain: str, from_version: str, to_version: str, fn: Callable[[str], str]
) -> None:
    """Registriert eine Migrationsfunktion."""
    _MIGRATIONS[(domain, from_version, to_version)] = fn


def merge_workflow_variants(
    default_variants: dict[str, dict[str, Any]],
    custom_variants: dict[str, dict[str, Any]] | None,
    tenant_id: str | None = None,
) -> dict[str, dict[str, Any]]:
    """
    Merge der Standard-Prozessvarianten mit tenant-spezifischen Overrides.
    Verwendet von finance_read_models und admin_core.
    """
    result = dict(default_variants)
    if custom_variants and isinstance(custom_variants, dict):
        for key, override in custom_variants.items():
            if isinstance(override, dict) and key in result:
                result[key] = {**result[key], **override}
            elif isinstance(override, dict):
                result[key] = dict(override)
    return result
