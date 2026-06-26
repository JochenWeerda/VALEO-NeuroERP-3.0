"""OPERATOR-AGENT-002 — Repository für persistente Agent-Proposals."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.infrastructure.models.agent_proposal_model import AgentProposalRecord
from app.services.operator_agent_service import AgentProposal, ApprovalStatus


class AgentProposalRepository:
    """Liest und schreibt AgentProposals in die Datenbank."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, tenant_id: str, proposal: AgentProposal) -> None:
        existing = self._db.get(AgentProposalRecord, proposal.proposal_id)
        if existing:
            existing.approval_status = proposal.approval_status.value
            existing.reviewed_at = proposal.reviewed_at
            existing.reviewed_by = proposal.reviewed_by
            existing.execution_result = proposal.execution_result
        else:
            record = AgentProposalRecord(
                proposal_id=proposal.proposal_id,
                tenant_id=tenant_id,
                action_type=proposal.action_type.value,
                risk_level=proposal.risk_level.value,
                approval_status=proposal.approval_status.value,
                context_snapshot=proposal.context_snapshot,
                rationale=proposal.rationale,
                idempotency_key=getattr(proposal, "idempotency_key", None),
                created_at=proposal.created_at,
                expires_at=proposal.expires_at,
            )
            self._db.add(record)
        self._db.commit()

    def get(self, tenant_id: str, proposal_id: str) -> AgentProposalRecord | None:
        rec = self._db.get(AgentProposalRecord, proposal_id)
        if rec and rec.tenant_id == tenant_id:
            return rec
        return None

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
