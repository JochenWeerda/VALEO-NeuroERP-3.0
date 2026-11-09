"""Reine Zuweisungsprüfung für LKW-Disposition — ohne I/O, ohne Mock-DB.

Der Drop in der Tafel ist nur UX. Persistenz und Domain-Event folgen erst,
wenn diese Prüfung keine Sperre liefert. Kontraktmengenbuchung gehört nicht
zum Drop: ``posts_quantity`` muss hier immer falsch sein.

Siehe ``docs/architecture/adaptive-workspace-disposition.md``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Literal

# Ist-Outbox-Typ; Soll-Annotation bleibt assignment_confirmed (workspace-events).
ASSIGNMENT_CONFIRMED_EVENT = "logistik.tour.created"
QUANTITY_POSTED_EVENT = "logistics.tour.quantity_posted"

REQUIRED_DISPATCH_PERMISSION = "logistics.write"
DISPATCH_ROLE_ALIASES = frozenset({
    "admin",
    "logistics",
    "logistics.write",
    "logistics:write",
    "dispatcher",
    "disponent",
    "fuhrpark",
})

Severity = Literal["blocking"]


def permissions_from_roles(roles: object) -> frozenset[str]:
    """Rechte nur aus Token-Rollen ableiten — nie aus dem Request-Body."""
    names = {str(role).lower().replace(":", ".") for role in (roles or [])}
    perms: set[str] = set()
    if names & {alias.replace(":", ".") for alias in DISPATCH_ROLE_ALIASES}:
        perms.add("logistics.write")
        perms.add("logistics.read")
    if "logistics.read" in names:
        perms.add("logistics.read")
    return frozenset(perms)


@dataclass(frozen=True)
class AssignmentIssue:
    code: str
    message: str
    severity: Severity = "blocking"


@dataclass(frozen=True)
class AssignmentContext:
    """Alles, was die Prüfung braucht — vom Aufrufer geladen, hier nur gelesen."""

    tenant_id: str
    actor_tenant_id: str
    actor_permissions: frozenset[str]
    order_id: str
    resource_id: str
    resource_tenant_id: str
    planned_start: datetime
    planned_end: datetime
    window_start: datetime
    window_end: datetime
    order_weight_kg: Decimal
    assigned_weight_kg: Decimal
    resource_capacity_kg: Decimal
    drop_quantity: Decimal
    contract_remaining_qty: Decimal
    allow_overdelivery: bool
    expected_version: int | None
    current_version: int | None
    approval_required: bool
    approval_granted: bool
    posts_quantity: bool = False
    abruf_id: str | None = None
    required_permission: str = REQUIRED_DISPATCH_PERMISSION


@dataclass(frozen=True)
class AssignmentDecision:
    ok: bool
    issues: tuple[AssignmentIssue, ...]
    event: str | None
    """Nur gesetzt, wenn die Zuweisung bestätigt werden darf. Nie quantity_posted."""

    persist_allowed: bool = False


def _qty(value: Decimal | int | float | str) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def validate_assignment(ctx: AssignmentContext) -> AssignmentDecision:
    """Prüft die Zuweisung vollständig, bevor irgendetwas persistiert wird."""
    issues: list[AssignmentIssue] = []

    if not ctx.tenant_id or ctx.tenant_id != ctx.actor_tenant_id:
        issues.append(AssignmentIssue(
            code="tenant_mismatch",
            message="Mandant der Sitzung und der Zuweisung stimmen nicht überein.",
        ))
    if ctx.resource_tenant_id != ctx.actor_tenant_id:
        issues.append(AssignmentIssue(
            code="resource_tenant_mismatch",
            message="Die Ressource gehört zu einem anderen Mandanten.",
        ))

    if ctx.required_permission not in ctx.actor_permissions:
        issues.append(AssignmentIssue(
            code="missing_permission",
            message="Für die Disposition fehlt das Schreibrecht.",
        ))

    if ctx.posts_quantity:
        issues.append(AssignmentIssue(
            code="quantity_post_on_drop_forbidden",
            message="Kontraktmengen werden nicht beim Drop gebucht, sondern erst beim fachlichen Buchungsereignis.",
        ))

    if ctx.planned_end <= ctx.planned_start:
        issues.append(AssignmentIssue(
            code="invalid_time_range",
            message="Das geplante Ende muss nach dem Start liegen.",
        ))
    if ctx.planned_start < ctx.window_start or ctx.planned_end > ctx.window_end:
        issues.append(AssignmentIssue(
            code="time_window_violation",
            message="Die geplante Tour liegt außerhalb des erlaubten Zeitfensters.",
        ))

    capacity = _qty(ctx.resource_capacity_kg)
    load = _qty(ctx.assigned_weight_kg) + _qty(ctx.order_weight_kg)
    if capacity <= 0:
        issues.append(AssignmentIssue(
            code="invalid_capacity",
            message="Die Ressourcenkapazität ist nicht gesetzt.",
        ))
    elif load > capacity:
        issues.append(AssignmentIssue(
            code="capacity_exceeded",
            message="Die Zuweisung würde die Fahrzeugkapazität überschreiten.",
        ))

    drop_qty = _qty(ctx.drop_quantity)
    remaining = _qty(ctx.contract_remaining_qty)
    if drop_qty <= 0:
        issues.append(AssignmentIssue(
            code="invalid_quantity",
            message="Die zuzuweisende Menge muss größer als null sein.",
        ))
    elif not ctx.allow_overdelivery and drop_qty > remaining:
        issues.append(AssignmentIssue(
            code="contract_quantity_exceeded",
            message="Die Zuweisung überschreitet die restliche Kontraktmenge.",
        ))

    if ctx.expected_version is not None and ctx.current_version is not None:
        if ctx.expected_version != ctx.current_version:
            issues.append(AssignmentIssue(
                code="concurrent_change",
                message="Die Ressource wurde inzwischen geändert. Bitte neu laden.",
            ))

    if ctx.approval_required and not ctx.approval_granted:
        issues.append(AssignmentIssue(
            code="approval_required",
            message="Die Zuweisung braucht eine Freigabe, bevor sie bestätigt wird.",
        ))

    if not ctx.order_id or not ctx.resource_id:
        issues.append(AssignmentIssue(
            code="incomplete_assignment",
            message="Auftrag und Ressource müssen beide gesetzt sein.",
        ))

    blocking = tuple(issue for issue in issues if issue.severity == "blocking")
    if blocking:
        return AssignmentDecision(ok=False, issues=blocking, event=None, persist_allowed=False)

    return AssignmentDecision(
        ok=True,
        issues=(),
        event=ASSIGNMENT_CONFIRMED_EVENT,
        persist_allowed=True,
    )


def quantity_posted_is_separate_event() -> str:
    """Der Buchungspfad — nicht der Drop. Nur zur Vertragssicherung."""
    return QUANTITY_POSTED_EVENT


@dataclass
class AssignmentCommand:
    """Transportobjekt für den Router. Die Prüfung bleibt rein."""

    context: AssignmentContext
    dry_run: bool = False
    extras: dict[str, str] = field(default_factory=dict)
