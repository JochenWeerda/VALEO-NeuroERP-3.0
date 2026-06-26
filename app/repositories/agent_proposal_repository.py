"""OPERATOR-AGENT-002 — Repository für persistente Agent-Proposals."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.infrastructure.models.agent_proposal_model import AgentProposalRecord
from app.services.operator_agent_service import (
    AgentActionType,
    AgentProposal,
    AgentRiskLevel,
    ApprovalStatus,
)


def proposal_to_snapshot(proposal: AgentProposal) -> dict[str, Any]:
    return {
        "context_summary": proposal.context_summary,
        "proposed_action": proposal.proposed_action,
        "human_approval_required": proposal.human_approval_required,
        "audit_events": proposal.audit_events,
        "rejection_reason": proposal.rejection_reason,
    }


def record_to_proposal(rec: AgentProposalRecord) -> AgentProposal:
    snap = rec.context_snapshot or {}
    approved_at = rec.reviewed_at if rec.approval_status == ApprovalStatus.APPROVED.value else None
    approved_by = rec.reviewed_by if rec.approval_status == ApprovalStatus.APPROVED.value else None
    return AgentProposal(
        proposal_id=rec.proposal_id,
        tenant_id=rec.tenant_id,
        action_type=AgentActionType(rec.action_type),
        risk_level=AgentRiskLevel(rec.risk_level),
        human_approval_required=bool(snap.get("human_approval_required", True)),
        context_summary=str(snap.get("context_summary", "")),
        proposed_action=str(snap.get("proposed_action", "")),
        rationale=rec.rationale or "",
        approval_status=ApprovalStatus(rec.approval_status),
        created_at=rec.created_at,
        approved_by=approved_by,
        approved_at=approved_at,
        rejection_reason=snap.get("rejection_reason"),
        audit_events=list(snap.get("audit_events") or []),
        idempotency_key=rec.idempotency_key,
        execution_result=rec.execution_result,
    )


class AgentProposalRepository:
    """Liest und schreibt AgentProposals in die Datenbank."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, tenant_id: str, proposal: AgentProposal) -> None:
        existing = self._db.get(AgentProposalRecord, proposal.proposal_id)
        reviewed_at = proposal.approved_at
        reviewed_by = proposal.approved_by
        if proposal.approval_status == ApprovalStatus.REJECTED and proposal.audit_events:
            last = proposal.audit_events[-1]
            if last.get("event") == "proposal_rejected":
                reviewed_by = last.get("rejected_by")
                reviewed_at = datetime.fromisoformat(last["occurred_at"])

        if existing:
            existing.approval_status = proposal.approval_status.value
            existing.context_snapshot = proposal_to_snapshot(proposal)
            existing.rationale = proposal.rationale
            existing.reviewed_at = reviewed_at
            existing.reviewed_by = reviewed_by
            existing.execution_result = proposal.execution_result
        else:
            record = AgentProposalRecord(
                proposal_id=proposal.proposal_id,
                tenant_id=tenant_id,
                action_type=proposal.action_type.value,
                risk_level=proposal.risk_level.value,
                approval_status=proposal.approval_status.value,
                context_snapshot=proposal_to_snapshot(proposal),
                rationale=proposal.rationale,
                idempotency_key=proposal.idempotency_key,
                created_at=proposal.created_at,
                expires_at=proposal.expires_at,
                reviewed_at=reviewed_at,
                reviewed_by=reviewed_by,
                execution_result=proposal.execution_result,
            )
            self._db.add(record)
        self._db.commit()

    def get(self, tenant_id: str, proposal_id: str) -> AgentProposalRecord | None:
        rec = self._db.get(AgentProposalRecord, proposal_id)
        if rec and rec.tenant_id == tenant_id:
            return rec
        return None

    def get_by_idempotency_key(self, tenant_id: str, idempotency_key: str) -> AgentProposalRecord | None:
        return (
            self._db.query(AgentProposalRecord)
            .filter(
                AgentProposalRecord.tenant_id == tenant_id,
                AgentProposalRecord.idempotency_key == idempotency_key,
            )
            .first()
        )

    def list(
        self,
        tenant_id: str,
        status: ApprovalStatus | None = None,
        limit: int = 100,
    ) -> list[AgentProposalRecord]:
        q = self._db.query(AgentProposalRecord).filter(
            AgentProposalRecord.tenant_id == tenant_id
        )
        if status:
            q = q.filter(AgentProposalRecord.approval_status == status.value)
        return q.order_by(AgentProposalRecord.created_at.desc()).limit(limit).all()

    def delete_expired(self, now: datetime | None = None) -> int:
        cutoff = now or datetime.now(timezone.utc)
        deleted = (
            self._db.query(AgentProposalRecord)
            .filter(
                AgentProposalRecord.expires_at.isnot(None),
                AgentProposalRecord.expires_at < cutoff,
                AgentProposalRecord.approval_status == ApprovalStatus.PENDING.value,
            )
            .delete(synchronize_session=False)
        )
        self._db.commit()
        return deleted
