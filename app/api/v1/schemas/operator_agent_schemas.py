"""Response-Schemas fuer den Operator-Agent (Vorschlag → Freigabe → Ausfuehrung).

SPEC-P1-06 Welle 3: ersetzt ``response_model=dict[str, Any]`` in
``app/api/v1/endpoints/operator_agent.py``.

Feldlisten aus ``AgentProposal.to_dict`` sowie ``read_context``, ``summary``
und ``execute_approved_action`` in ``operator_agent_service``.

``context`` und ``result`` bleiben offene ``dict``-Felder: ihr Inhalt haengt am
``action_type`` (Mahnung, Rechnung, QS-Freigabe, …) und ist je Aktion anders
aufgebaut. Der Rahmen der Antwort — und damit der Sicherheitsvertrag aus
Risikostufe und Freigabepflicht — ist vollstaendig typisiert.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


class AgentContextOut(BaseSchema):
    """``POST /context`` — Lesezugriff ohne Schreibwirkung."""

    tenant_id: Optional[str] = None
    action_type: Optional[str] = None
    risk_level: Optional[str] = Field(default=None, description="Risikostufe der Aktion")
    human_approval_required: Optional[bool] = Field(
        default=None, description="True, wenn die Aktion eine menschliche Freigabe braucht"
    )
    context: dict[str, Any] = Field(
        default_factory=dict, description="Aktionsspezifischer Lesekontext"
    )
    retrieved_at: Optional[str] = None
    hinweis: Optional[str] = None


class AgentProposalOut(BaseSchema):
    """Agent-Proposal — Ergebnis von Anlage, Detail, Freigabe und Ablehnung.

    Entspricht ``AgentProposal.to_dict``.
    """

    proposal_id: Optional[str] = None
    tenant_id: Optional[str] = None
    action_type: Optional[str] = None
    risk_level: Optional[str] = None
    human_approval_required: Optional[bool] = None
    context_summary: Optional[Any] = None
    proposed_action: Optional[Any] = None
    rationale: Optional[str] = None
    approval_status: Optional[str] = None
    created_at: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    rejection_reason: Optional[str] = None
    audit_event_count: Optional[int] = Field(
        default=None, description="Anzahl der Audit-Ereignisse am Proposal"
    )


class AgentProposalSummaryOut(BaseSchema):
    """``GET /proposals/summary``"""

    tenant_id: Optional[str] = None
    total_proposals: Optional[int] = None
    by_status: dict[str, int] = Field(
        default_factory=dict, description="Anzahl je Freigabestatus"
    )
    pending_high_risk: Optional[int] = Field(
        default=None, description="Offene Vorschlaege mit hoher Risikostufe"
    )


class AgentExecutionOut(BaseSchema):
    """``POST /proposals/{id}/execute`` — nur fuer genehmigte LOW-Risiko-Aktionen."""

    proposal_id: Optional[str] = None
    action_type: Optional[str] = None
    executed_by: Optional[str] = None
    executed_at: Optional[str] = None
    result: dict[str, Any] = Field(
        default_factory=dict, description="Aktionsspezifisches Ausfuehrungsergebnis"
    )
