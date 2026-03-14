"""
Explainability models for workflow and policy-backed decisions.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.core.policy_decisions import PolicyOverrideResolution


ExplainabilityDecisionStatus = Literal["allowed", "blocked", "approval-required", "exception"]


class ExplainabilityDetail(BaseModel):
    label: str = Field(min_length=1)
    value: str = Field(min_length=1)


class ExplainabilityView(BaseModel):
    status: ExplainabilityDecisionStatus
    summary: str = Field(min_length=1)
    rule_id: str | None = None
    reason: str | None = None
    source_scope: str | None = None
    details: list[ExplainabilityDetail] = Field(default_factory=list)


def build_policy_explainability_view(
    resolution: PolicyOverrideResolution,
    *,
    blocked: bool = False,
    needs_approval: bool = False,
) -> ExplainabilityView:
    status: ExplainabilityDecisionStatus = "allowed"
    summary = "Aktion ist zulässig."
    if blocked:
        status = "blocked"
        summary = "Aktion ist durch Regel oder Override blockiert."
    elif needs_approval:
        status = "approval-required"
        summary = "Aktion ist zulässig, benötigt aber Freigabe."

    details: list[ExplainabilityDetail] = []
    if resolution.effective_scope:
        details.append(ExplainabilityDetail(label="Wirksame Ebene", value=resolution.effective_scope))
    if resolution.effective_scope_key:
        details.append(ExplainabilityDetail(label="Ebene", value=resolution.effective_scope_key))
    if resolution.applied_reason:
        details.append(ExplainabilityDetail(label="Grund", value=resolution.applied_reason))
    if resolution.applied_source:
        details.append(ExplainabilityDetail(label="Quelle", value=resolution.applied_source))

    return ExplainabilityView(
        status=status,
        summary=summary,
        rule_id=resolution.rule_id,
        reason=resolution.applied_reason,
        source_scope=resolution.effective_scope,
        details=details,
    )
