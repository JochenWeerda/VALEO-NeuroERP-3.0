"""
Case Management Service — NC-08
Verwaltung offener Freigabe-Cases fuer Human Oversight.
Baut auf human_approval_gate.py auf und ergaenzt:
- Case-Lifecycle (open -> assigned -> decided -> closed)
- Eskalation bei Timeout
- Case-Suche und Dashboard-Daten
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from app.core.human_approval_gate import (
    ApprovalDecision,
    ApprovalRisikostufe,
    HumanApprovalRequirement,
    record_approval_decision,
)

logger = logging.getLogger(__name__)


class CaseStatus(str, Enum):
    OPEN = "open"
    ASSIGNED = "assigned"
    DECIDED = "decided"
    ESCALATED = "escalated"
    EXPIRED = "expired"
    CLOSED = "closed"


class CasePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


_RISIKO_TO_PRIORITY: dict[ApprovalRisikostufe, CasePriority] = {
    ApprovalRisikostufe.NIEDRIG: CasePriority.LOW,
    ApprovalRisikostufe.MITTEL: CasePriority.MEDIUM,
    ApprovalRisikostufe.HOCH: CasePriority.HIGH,
    ApprovalRisikostufe.KRITISCH: CasePriority.CRITICAL,
}

_PRIORITY_SLA_HOURS: dict[CasePriority, int] = {
    CasePriority.LOW: 72,
    CasePriority.MEDIUM: 24,
    CasePriority.HIGH: 4,
    CasePriority.CRITICAL: 1,
}


@dataclass
class ApprovalCase:
    case_id: str = field(default_factory=lambda: str(uuid4()))
    status: CaseStatus = CaseStatus.OPEN
    priority: CasePriority = CasePriority.MEDIUM
    aktions_typ: str = ""
    instanz_id: str = ""
    agent_id: str = ""
    risiko_stufe: str = ""
    begruendung: str = ""
    freigabe_rolle: str = ""
    assigned_to: Optional[str] = None
    decision: Optional[str] = None
    decision_comment: Optional[str] = None
    decided_by: Optional[str] = None
    decided_at: Optional[str] = None
    context: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    due_at: Optional[str] = None
    escalated_to: Optional[str] = None
    tenant_id: str = "system"

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "status": self.status.value,
            "priority": self.priority.value,
            "aktions_typ": self.aktions_typ,
            "instanz_id": self.instanz_id,
            "agent_id": self.agent_id,
            "risiko_stufe": self.risiko_stufe,
            "begruendung": self.begruendung,
            "freigabe_rolle": self.freigabe_rolle,
            "assigned_to": self.assigned_to,
            "decision": self.decision,
            "decision_comment": self.decision_comment,
            "decided_by": self.decided_by,
            "decided_at": self.decided_at,
            "created_at": self.created_at,
            "due_at": self.due_at,
            "escalated_to": self.escalated_to,
            "tenant_id": self.tenant_id,
        }

    @property
    def is_overdue(self) -> bool:
        if not self.due_at or self.status in (CaseStatus.DECIDED, CaseStatus.CLOSED):
            return False
        try:
            due = datetime.fromisoformat(self.due_at)
            return datetime.now(timezone.utc) > due
        except ValueError:
            return False


_CASE_STORE: dict[str, ApprovalCase] = {}


def create_case(
    requirement: HumanApprovalRequirement,
    instanz_id: str,
    agent_id: str,
    context: dict[str, Any],
    tenant_id: str = "system",
) -> ApprovalCase:
    priority = _RISIKO_TO_PRIORITY.get(
        ApprovalRisikostufe(requirement.risiko_stufe.value
                            if hasattr(requirement.risiko_stufe, 'value')
                            else requirement.risiko_stufe),
        CasePriority.MEDIUM,
    )
    sla_hours = _PRIORITY_SLA_HOURS[priority]
    due_at = (datetime.now(timezone.utc) + timedelta(hours=sla_hours)).isoformat()

    case = ApprovalCase(
        priority=priority,
        aktions_typ=requirement.aktions_typ,
        instanz_id=instanz_id,
        agent_id=agent_id,
        risiko_stufe=requirement.risiko_stufe.value if hasattr(requirement.risiko_stufe, 'value') else requirement.risiko_stufe,
        begruendung=requirement.begruendung,
        freigabe_rolle=requirement.freigabe_rolle,
        context=context,
        due_at=due_at,
        tenant_id=tenant_id,
    )
    _CASE_STORE[case.case_id] = case
    logger.info(
        "Case %s erstellt: %s (Prioritaet: %s, SLA: %sh)",
        case.case_id, case.aktions_typ, priority.value, sla_hours,
    )
    return case


def assign_case(case_id: str, user_id: str) -> Optional[ApprovalCase]:
    case = _CASE_STORE.get(case_id)
    if not case or case.status not in (CaseStatus.OPEN, CaseStatus.ESCALATED):
        return None
    case.status = CaseStatus.ASSIGNED
    case.assigned_to = user_id
    logger.info("Case %s zugewiesen an %s", case_id, user_id)
    return case


def decide_case(
    case_id: str,
    decision: ApprovalDecision,
    decided_by: str,
    comment: str = "",
) -> Optional[ApprovalCase]:
    case = _CASE_STORE.get(case_id)
    if not case or case.status in (CaseStatus.DECIDED, CaseStatus.CLOSED):
        return None

    case.status = CaseStatus.DECIDED
    case.decision = decision.value
    case.decided_by = decided_by
    case.decided_at = datetime.now(timezone.utc).isoformat()
    case.decision_comment = comment

    record_approval_decision(
        aktions_typ=case.aktions_typ,
        instanz_id=case.instanz_id,
        agent_id=case.agent_id,
        risiko_stufe=ApprovalRisikostufe(case.risiko_stufe),
        decision=decision,
        entschieden_von=decided_by,
        begruendung=comment or case.begruendung,
        kontext=case.context,
    )

    logger.info("Case %s entschieden: %s von %s", case_id, decision.value, decided_by)
    return case


def escalate_case(case_id: str, escalate_to: str, reason: str = "") -> Optional[ApprovalCase]:
    case = _CASE_STORE.get(case_id)
    if not case or case.status in (CaseStatus.DECIDED, CaseStatus.CLOSED):
        return None

    case.status = CaseStatus.ESCALATED
    case.escalated_to = escalate_to
    case.priority = CasePriority.CRITICAL
    logger.info("Case %s eskaliert an %s: %s", case_id, escalate_to, reason)
    return case


def close_case(case_id: str) -> Optional[ApprovalCase]:
    case = _CASE_STORE.get(case_id)
    if not case:
        return None
    case.status = CaseStatus.CLOSED
    return case


def get_case(case_id: str) -> Optional[ApprovalCase]:
    return _CASE_STORE.get(case_id)


def list_cases(
    status: Optional[CaseStatus] = None,
    priority: Optional[CasePriority] = None,
    assigned_to: Optional[str] = None,
    tenant_id: Optional[str] = None,
    limit: int = 100,
) -> list[ApprovalCase]:
    results = list(_CASE_STORE.values())
    if status:
        results = [c for c in results if c.status == status]
    if priority:
        results = [c for c in results if c.priority == priority]
    if assigned_to:
        results = [c for c in results if c.assigned_to == assigned_to]
    if tenant_id:
        results = [c for c in results if c.tenant_id == tenant_id]
    results.sort(key=lambda c: (
        {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(c.priority.value, 9),
        c.created_at,
    ))
    return results[:limit]


def get_dashboard_stats(tenant_id: Optional[str] = None) -> dict[str, Any]:
    cases = list(_CASE_STORE.values())
    if tenant_id:
        cases = [c for c in cases if c.tenant_id == tenant_id]

    open_count = sum(1 for c in cases if c.status in (CaseStatus.OPEN, CaseStatus.ASSIGNED, CaseStatus.ESCALATED))
    overdue_count = sum(1 for c in cases if c.is_overdue)

    by_priority = {}
    for p in CasePriority:
        by_priority[p.value] = sum(1 for c in cases if c.priority == p and c.status not in (CaseStatus.DECIDED, CaseStatus.CLOSED))

    by_status = {}
    for s in CaseStatus:
        by_status[s.value] = sum(1 for c in cases if c.status == s)

    return {
        "total": len(cases),
        "open": open_count,
        "overdue": overdue_count,
        "by_priority": by_priority,
        "by_status": by_status,
    }


def check_and_escalate_overdue() -> list[ApprovalCase]:
    escalated = []
    for case in _CASE_STORE.values():
        if case.is_overdue and case.status in (CaseStatus.OPEN, CaseStatus.ASSIGNED):
            case.status = CaseStatus.ESCALATED
            case.priority = CasePriority.CRITICAL
            escalated.append(case)
            logger.warning("Case %s automatisch eskaliert (SLA ueberschritten)", case.case_id)
    return escalated
