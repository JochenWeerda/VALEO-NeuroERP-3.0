"""
Settlement Approval Flow — Wave 19 AP1

Freigabe-Zustandsmaschine fuer Abrechnungen (Agrar-Settlement).
Integriert Canonical Process Definitions (Wave 18), Audit-Contracts und
den Human-Gate fuer KI-Agenten.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime, timezone


class SettlementApprovalStatus(str, Enum):
    ENTWURF = "ENTWURF"
    ZUR_FREIGABE = "ZUR_FREIGABE"
    TEILWEISE_FREIGEGEBEN = "TEILWEISE_FREIGEGEBEN"
    FREIGEGEBEN = "FREIGEGEBEN"
    ABGELEHNT = "ABGELEHNT"
    VERBUCHT = "VERBUCHT"


class SettlementActorType(str, Enum):
    SACHBEARBEITER = "SACHBEARBEITER"
    ABTEILUNGSLEITER = "ABTEILUNGSLEITER"
    PROKURIST = "PROKURIST"
    AGENT = "AGENT"
    SYSTEM = "SYSTEM"


@dataclass
class SettlementApprovalRequest:
    """Request to advance a settlement through the approval flow."""

    settlement_id: str
    tenant_id: str
    actor_id: str
    actor_type: SettlementActorType
    target_status: SettlementApprovalStatus
    reason: Optional[str] = None
    # Wave-18 Canonical Process Metadata
    process_definition_key: str = "agrar_settlement"
    workflow_version: str = "1.0"
    # Audit
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SettlementApprovalResult:
    """Result of an approval step."""

    settlement_id: str
    previous_status: SettlementApprovalStatus
    new_status: SettlementApprovalStatus
    allowed: bool
    reason: str
    actor_id: str
    actor_type: SettlementActorType
    process_definition_key: str = "agrar_settlement"
    workflow_version: str = "1.0"
    decided_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def audit_entry(self) -> dict:
        return {
            "settlement_id": self.settlement_id,
            "event": f"settlement.approval.{self.new_status.lower()}",
            "process_definition_key": self.process_definition_key,
            "workflow_version": self.workflow_version,
            "actor_id": self.actor_id,
            "actor_type": self.actor_type.value,
            "previous_status": self.previous_status.value,
            "new_status": self.new_status.value,
            "allowed": self.allowed,
            "reason": self.reason,
            "decided_at": self.decided_at.isoformat(),
        }


# ---------------------------------------------------------------------------
# Transition rules
# ---------------------------------------------------------------------------

_ALLOWED_TRANSITIONS: dict[SettlementApprovalStatus, list[SettlementApprovalStatus]] = {
    SettlementApprovalStatus.ENTWURF: [
        SettlementApprovalStatus.ZUR_FREIGABE,
        SettlementApprovalStatus.ABGELEHNT,
    ],
    SettlementApprovalStatus.ZUR_FREIGABE: [
        SettlementApprovalStatus.TEILWEISE_FREIGEGEBEN,
        SettlementApprovalStatus.FREIGEGEBEN,
        SettlementApprovalStatus.ABGELEHNT,
        SettlementApprovalStatus.ENTWURF,  # Rueckzug erlaubt
    ],
    SettlementApprovalStatus.TEILWEISE_FREIGEGEBEN: [
        SettlementApprovalStatus.FREIGEGEBEN,
        SettlementApprovalStatus.ABGELEHNT,
        SettlementApprovalStatus.ZUR_FREIGABE,  # Neustart moeglich
    ],
    SettlementApprovalStatus.FREIGEGEBEN: [
        SettlementApprovalStatus.VERBUCHT,
        SettlementApprovalStatus.ABGELEHNT,  # Nachtraeglicher Widerruf
    ],
    SettlementApprovalStatus.ABGELEHNT: [
        SettlementApprovalStatus.ENTWURF,  # Ueberarbeitung
    ],
    SettlementApprovalStatus.VERBUCHT: [],  # Terminal
}

# Mindest-Aktor fuer bestimmte Uebergaenge
_REQUIRED_ACTOR: dict[SettlementApprovalStatus, set[SettlementActorType]] = {
    SettlementApprovalStatus.FREIGEGEBEN: {
        SettlementActorType.ABTEILUNGSLEITER,
        SettlementActorType.PROKURIST,
        SettlementActorType.SYSTEM,
    },
    SettlementApprovalStatus.VERBUCHT: {
        SettlementActorType.SACHBEARBEITER,
        SettlementActorType.ABTEILUNGSLEITER,
        SettlementActorType.PROKURIST,
        SettlementActorType.SYSTEM,
    },
}


def evaluate_settlement_approval(
    request: SettlementApprovalRequest,
    current_status: SettlementApprovalStatus,
) -> SettlementApprovalResult:
    """
    Evaluate whether the requested status transition is permitted.

    Rules:
    1. Transition must be in the allowed set for the current status.
    2. Certain target statuses require a minimum actor role.
    3. AGENT actors may never directly transition to VERBUCHT (Human-Gate).
    """
    target = request.target_status

    # Rule 1: valid transition?
    if target not in _ALLOWED_TRANSITIONS.get(current_status, []):
        return SettlementApprovalResult(
            settlement_id=request.settlement_id,
            previous_status=current_status,
            new_status=current_status,
            allowed=False,
            reason=(
                f"Uebergang {current_status.value} -> {target.value} "
                "ist nicht zulaessig."
            ),
            actor_id=request.actor_id,
            actor_type=request.actor_type,
            process_definition_key=request.process_definition_key,
            workflow_version=request.workflow_version,
        )

    # Rule 2: actor role sufficient?
    required = _REQUIRED_ACTOR.get(target)
    if required and request.actor_type not in required:
        return SettlementApprovalResult(
            settlement_id=request.settlement_id,
            previous_status=current_status,
            new_status=current_status,
            allowed=False,
            reason=(
                f"Aktor-Typ {request.actor_type.value} hat keine Berechtigung "
                f"fuer Zielstatus {target.value}. "
                f"Erforderlich: {', '.join(a.value for a in required)}."
            ),
            actor_id=request.actor_id,
            actor_type=request.actor_type,
            process_definition_key=request.process_definition_key,
            workflow_version=request.workflow_version,
        )

    # Rule 3: Human-Gate — AGENT darf nie selbst auf VERBUCHT setzen
    if (
        request.actor_type == SettlementActorType.AGENT
        and target == SettlementApprovalStatus.VERBUCHT
    ):
        return SettlementApprovalResult(
            settlement_id=request.settlement_id,
            previous_status=current_status,
            new_status=current_status,
            allowed=False,
            reason=(
                "Human-Gate: KI-Agenten duerfen Abrechnungen nicht selbst verbuchen. "
                "Menschliche Freigabe durch Sachbearbeiter oder Abteilungsleiter erforderlich."
            ),
            actor_id=request.actor_id,
            actor_type=request.actor_type,
            process_definition_key=request.process_definition_key,
            workflow_version=request.workflow_version,
        )

    return SettlementApprovalResult(
        settlement_id=request.settlement_id,
        previous_status=current_status,
        new_status=target,
        allowed=True,
        reason=f"Freigabe erteilt: {current_status.value} -> {target.value}.",
        actor_id=request.actor_id,
        actor_type=request.actor_type,
        process_definition_key=request.process_definition_key,
        workflow_version=request.workflow_version,
    )


def get_allowed_transitions(
    current_status: SettlementApprovalStatus,
) -> list[SettlementApprovalStatus]:
    """Return the list of reachable statuses from the current status."""
    return list(_ALLOWED_TRANSITIONS.get(current_status, []))


def is_terminal(status: SettlementApprovalStatus) -> bool:
    """Return True if no further transitions are possible."""
    return not _ALLOWED_TRANSITIONS.get(status)
