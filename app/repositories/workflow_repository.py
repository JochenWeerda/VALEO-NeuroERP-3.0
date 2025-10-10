"""
Workflow Repository
Status & Audit-Operations für Workflows
"""

from __future__ import annotations
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
import uuid
import time

from app.models.documents import WorkflowStatus, WorkflowAudit


class WorkflowRepository:
    """Repository für Workflow-Status & Audit"""

    def __init__(self, db: Session):
        self.db = db

    def get_status(self, domain: str, doc_number: str) -> str:
        """Holt aktuellen Status"""
        stmt = select(WorkflowStatus).where(
            WorkflowStatus.domain == domain, WorkflowStatus.doc_number == doc_number
        )
        status = self.db.execute(stmt).scalar_one_or_none()
        return status.state if status else 'draft'

    def set_status(
        self, domain: str, doc_number: str, state: str, user: Optional[str] = None
    ) -> None:
        """Setzt Status"""
        stmt = select(WorkflowStatus).where(
            WorkflowStatus.domain == domain, WorkflowStatus.doc_number == doc_number
        )
        status = self.db.execute(stmt).scalar_one_or_none()

        if status:
            status.state = state
            status.updated_by = user
        else:
            status = WorkflowStatus(
                id=str(uuid.uuid4()),
                domain=domain,
                doc_number=doc_number,
                state=state,
                updated_by=user,
            )
            self.db.add(status)

        self.db.commit()

    def add_audit(
        self,
        domain: str,
        doc_number: str,
        from_state: str,
        to_state: str,
        action: str,
        user: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        """Fügt Audit-Eintrag hinzu"""
        audit = WorkflowAudit(
            id=str(uuid.uuid4()),
            domain=domain,
            doc_number=doc_number,
            ts=int(time.time()),
            from_state=from_state,
            to_state=to_state,
            action=action,
            user=user,
            reason=reason,
        )
        self.db.add(audit)
        self.db.commit()

    def get_audit(self, domain: str, doc_number: str) -> List[WorkflowAudit]:
        """Holt Audit-Trail"""
        stmt = (
            select(WorkflowAudit)
            .where(
                WorkflowAudit.domain == domain, WorkflowAudit.doc_number == doc_number
            )
            .order_by(WorkflowAudit.ts.asc())
        )
        return list(self.db.execute(stmt).scalars().all())

