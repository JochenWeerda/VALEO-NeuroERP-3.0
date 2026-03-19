"""
Workflow Repository
Status & Audit-Operations für Workflows
"""

from __future__ import annotations

import time
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7
from app.core.workflow_definitions import migrate_state
from app.models.documents import WorkflowAudit, WorkflowStatus


class WorkflowRepository:
    """Repository für Workflow-Status & Audit"""

    def __init__(self, db: Session):
        self.db = db

    def get_status(self, domain: str, doc_number: str) -> str:
        """Holt aktuellen Status (Gap 011: compatibility)."""
        state, _ = self.get_status_with_version(domain, doc_number)
        return state

    def get_status_with_version(
        self, domain: str, doc_number: str
    ) -> tuple[str, str]:
        """Holt aktuellen Status und workflow_version (Gap 011)."""
        stmt = select(WorkflowStatus).where(
            WorkflowStatus.domain == domain, WorkflowStatus.doc_number == doc_number
        )
        status = self.db.execute(stmt).scalar_one_or_none()
        if not status:
            return ("draft", "1")
        version = getattr(status, "workflow_version", None) or "1"
        return (status.state, str(version))

    def set_status(
        self,
        domain: str,
        doc_number: str,
        state: str,
        user: Optional[str] = None,
        workflow_version: Optional[str] = None,
    ) -> None:
        """Setzt Status. Bei neuem Eintrag optional workflow_version (Gap 011)."""
        stmt = select(WorkflowStatus).where(
            WorkflowStatus.domain == domain, WorkflowStatus.doc_number == doc_number
        )
        status = self.db.execute(stmt).scalar_one_or_none()

        if status:
            status.state = state
            status.updated_by = user
        else:
            status = WorkflowStatus(
                id=uuid7(),
                domain=domain,
                doc_number=doc_number,
                state=state,
                workflow_version=workflow_version or "1",
                updated_by=user,
            )
            self.db.add(status)

        self.db.commit()

    def migrate_to_version(
        self, domain: str, doc_number: str, target_version: str
    ) -> bool:
        """
        Migriert eine Workflow-Instanz auf eine neue Version (Gap 011).
        Returns True wenn migriert, False wenn Instanz nicht existiert.
        """
        stmt = select(WorkflowStatus).where(
            WorkflowStatus.domain == domain, WorkflowStatus.doc_number == doc_number
        )
        status = self.db.execute(stmt).scalar_one_or_none()
        if not status:
            return False
        from_version = getattr(status, "workflow_version", None) or "1"
        if from_version == target_version:
            return True
        new_state = migrate_state(domain, from_version, target_version, status.state)
        status.state = new_state
        status.workflow_version = target_version
        self.db.commit()
        return True

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
            id=uuid7(),
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

