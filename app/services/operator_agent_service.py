"""OPERATOR-AGENT-001 — Read-Only/Proposal-Modus fuer ERP-Operator-Agent.

Kein autonomes Schreiben. Agenten-Aktionen:
- Kontext lesen (OP-Liste, Mahnstatus, QS-Sperren, Gate-Status)
- Handlung vorschlagen (Mahnvorschlag, Rechnungsvorschlag, QS-Freigabevorschlag)
- Human-Approval-Request erzeugen und protokollieren
- Audit-Event schreiben

Jede Aktion hat einen definierten Risiko-Level und einen Human-Approval-Schwellwert.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class AgentActionType(str, Enum):
    MAHNUNG_VORSCHLAG = "mahnung_vorschlag"
    RECHNUNG_VORSCHLAG = "rechnung_vorschlag"
    QS_FREIGABE_VORSCHLAG = "qs_freigabe_vorschlag"
    OFFENE_GATES_ABFRAGE = "offene_gates_abfrage"
    ANGEBOTSNACHFASSUNG = "angebotsnachfassung"
    DMS_PAKET_VORSCHLAG = "dms_paket_vorschlag"


class AgentRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


_RISK_BY_ACTION: dict[AgentActionType, AgentRiskLevel] = {
    AgentActionType.MAHNUNG_VORSCHLAG: AgentRiskLevel.HIGH,
    AgentActionType.RECHNUNG_VORSCHLAG: AgentRiskLevel.HIGH,
    AgentActionType.QS_FREIGABE_VORSCHLAG: AgentRiskLevel.HIGH,
    AgentActionType.OFFENE_GATES_ABFRAGE: AgentRiskLevel.LOW,
    AgentActionType.ANGEBOTSNACHFASSUNG: AgentRiskLevel.MEDIUM,
    AgentActionType.DMS_PAKET_VORSCHLAG: AgentRiskLevel.MEDIUM,
}

_HUMAN_APPROVAL_REQUIRED: set[AgentActionType] = {
    AgentActionType.MAHNUNG_VORSCHLAG,
    AgentActionType.RECHNUNG_VORSCHLAG,
    AgentActionType.QS_FREIGABE_VORSCHLAG,
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class AgentProposal:
    proposal_id: str
    tenant_id: str
    action_type: AgentActionType
    risk_level: AgentRiskLevel
    human_approval_required: bool
    context_summary: str
    proposed_action: str
    rationale: str
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = field(default_factory=_utcnow)
    approved_by: str | None = None
    approved_at: datetime | None = None
    rejection_reason: str | None = None
    audit_events: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "tenant_id": self.tenant_id,
            "action_type": self.action_type.value,
            "risk_level": self.risk_level.value,
            "human_approval_required": self.human_approval_required,
            "context_summary": self.context_summary,
            "proposed_action": self.proposed_action,
            "rationale": self.rationale,
            "approval_status": self.approval_status.value,
            "created_at": self.created_at.isoformat(),
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "rejection_reason": self.rejection_reason,
            "audit_event_count": len(self.audit_events),
        }


class OperatorAgentPermissionError(PermissionError):
    """Keine agent:read oder agent:propose Berechtigung."""


class ProposalNotFoundError(LookupError):
    """Proposal-ID nicht gefunden fuer diesen Tenant."""


class OperatorAgentService:
    """Read-Only/Proposal-Modus fuer den ERP-Operator-Agent."""

    def __init__(self) -> None:
        self._proposals: dict[tuple[str, str], AgentProposal] = {}

    def _require_role(self, roles: set[str], required: str) -> None:
        if required not in roles:
            raise OperatorAgentPermissionError(f"Rolle '{required}' erforderlich")

    def read_context(
        self,
        *,
        tenant_id: str,
        action_type: AgentActionType,
        roles: set[str],
        query_params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self._require_role(roles, "agent:read")
        risk = _RISK_BY_ACTION[action_type]
        return {
            "tenant_id": tenant_id,
            "action_type": action_type.value,
            "risk_level": risk.value,
            "human_approval_required": action_type in _HUMAN_APPROVAL_REQUIRED,
            "context": self._simulate_context(action_type, query_params or {}),
            "retrieved_at": _utcnow().isoformat(),
            "hinweis": "Kontext-Abfrage — kein Schreibzugriff.",
        }

    def _simulate_context(self, action_type: AgentActionType, params: dict[str, Any]) -> dict[str, Any]:
        if action_type == AgentActionType.MAHNUNG_VORSCHLAG:
            return {
                "faellige_ops": [
                    {"beleg_nr": "RE-2026-001", "kunden_nr": params.get("kunden_nr", "K-001"),
                     "betrag_eur": 1234.56, "faellig_am": "2026-06-10", "mahnstufe": 0},
                ],
                "gesamt_offen_eur": 1234.56,
                "empfohlene_mahnstufe": 1,
            }
        if action_type == AgentActionType.RECHNUNG_VORSCHLAG:
            return {
                "offene_lieferscheine": [
                    {"ls_nr": "LS-2026-042", "kunden_nr": params.get("kunden_nr", "K-001"),
                     "positionen": 3, "netto_eur": 4567.89},
                ],
            }
        if action_type == AgentActionType.QS_FREIGABE_VORSCHLAG:
            return {
                "lots_in_pruefung": [
                    {"lot_id": params.get("lot_id", "LOT-001"), "artikel": "Weizen A",
                     "menge_kg": 25000, "qs_status": "in_pruefung"},
                ],
            }
        if action_type == AgentActionType.OFFENE_GATES_ABFRAGE:
            return {
                "gates": [
                    {"gate_typ": "elster", "status": "offen", "faellig_am": "2026-07-10"},
                    {"gate_typ": "datev", "status": "abgenommen", "faellig_am": None},
                ],
            }
        if action_type == AgentActionType.ANGEBOTSNACHFASSUNG:
            return {
                "offene_angebote": [
                    {"angebot_nr": "ANG-2026-007", "kunden_nr": params.get("kunden_nr", "K-001"),
                     "wert_eur": 9876.0, "gueltig_bis": "2026-06-30"},
                ],
            }
        return {}

    def create_proposal(
        self,
        *,
        tenant_id: str,
        action_type: AgentActionType,
        roles: set[str],
        context_summary: str,
        proposed_action: str,
        rationale: str,
    ) -> AgentProposal:
        self._require_role(roles, "agent:propose")
        risk = _RISK_BY_ACTION[action_type]
        proposal = AgentProposal(
            proposal_id=str(uuid4()),
            tenant_id=tenant_id,
            action_type=action_type,
            risk_level=risk,
            human_approval_required=action_type in _HUMAN_APPROVAL_REQUIRED,
            context_summary=context_summary,
            proposed_action=proposed_action,
            rationale=rationale,
        )
        proposal.audit_events.append({
            "event": "proposal_created",
            "occurred_at": _utcnow().isoformat(),
        })
        self._proposals[(tenant_id, proposal.proposal_id)] = proposal
        return proposal

    def get_proposal(self, *, tenant_id: str, proposal_id: str) -> AgentProposal:
        proposal = self._proposals.get((tenant_id, proposal_id))
        if proposal is None:
            raise ProposalNotFoundError(proposal_id)
        return proposal

    def list_proposals(self, *, tenant_id: str, status: ApprovalStatus | None = None) -> list[AgentProposal]:
        results = [p for (t, _), p in self._proposals.items() if t == tenant_id]
        if status is not None:
            results = [p for p in results if p.approval_status == status]
        return sorted(results, key=lambda p: p.created_at, reverse=True)

    def approve_proposal(
        self,
        *,
        tenant_id: str,
        proposal_id: str,
        approved_by: str,
        roles: set[str],
    ) -> AgentProposal:
        self._require_role(roles, "agent:approve")
        proposal = self.get_proposal(tenant_id=tenant_id, proposal_id=proposal_id)
        if proposal.approval_status != ApprovalStatus.PENDING:
            raise ValueError(f"Proposal ist bereits {proposal.approval_status.value}")
        proposal.approval_status = ApprovalStatus.APPROVED
        proposal.approved_by = approved_by
        proposal.approved_at = _utcnow()
        proposal.audit_events.append({
            "event": "proposal_approved",
            "approved_by": approved_by,
            "occurred_at": proposal.approved_at.isoformat(),
        })
        return proposal

    def reject_proposal(
        self,
        *,
        tenant_id: str,
        proposal_id: str,
        rejected_by: str,
        reason: str,
        roles: set[str],
    ) -> AgentProposal:
        self._require_role(roles, "agent:approve")
        proposal = self.get_proposal(tenant_id=tenant_id, proposal_id=proposal_id)
        if proposal.approval_status != ApprovalStatus.PENDING:
            raise ValueError(f"Proposal ist bereits {proposal.approval_status.value}")
        proposal.approval_status = ApprovalStatus.REJECTED
        proposal.rejection_reason = reason
        proposal.audit_events.append({
            "event": "proposal_rejected",
            "rejected_by": rejected_by,
            "reason": reason,
            "occurred_at": _utcnow().isoformat(),
        })
        return proposal

    def summary(self, *, tenant_id: str) -> dict[str, Any]:
        proposals = self.list_proposals(tenant_id=tenant_id)
        by_status: dict[str, int] = {s.value: 0 for s in ApprovalStatus}
        for p in proposals:
            by_status[p.approval_status.value] += 1
        return {
            "tenant_id": tenant_id,
            "total_proposals": len(proposals),
            "by_status": by_status,
            "pending_high_risk": sum(
                1 for p in proposals
                if p.approval_status == ApprovalStatus.PENDING
                and p.risk_level == AgentRiskLevel.HIGH
            ),
        }


operator_agent_service = OperatorAgentService()
