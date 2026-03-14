"""
Exception, deduction and complaint rule models for the process kernel.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.core.settlement_compatibility import (
    CANONICAL_SETTLEMENT_AGGREGATE,
    CANONICAL_SETTLEMENT_PROCESS_DEFINITION_KEY,
)


ExceptionCategory = Literal["complaint", "deduction", "quality-deviation", "manual-override"]
ExceptionDecisionMode = Literal["policy", "workflow-approval", "manual-approval", "informational"]


class ProcessExceptionRule(BaseModel):
    rule_id: str = Field(min_length=1)
    category: ExceptionCategory
    trigger_key: str = Field(min_length=1)
    decision_mode: ExceptionDecisionMode
    requires_approval: bool = False
    approver_roles: list[str] = Field(default_factory=list)
    policy_rule_id: str | None = None
    description: str = Field(min_length=1)


class ProcessExceptionCatalog(BaseModel):
    process_key: str = Field(min_length=1)
    canonical_aggregate_type: str | None = None
    canonical_process_definition_key: str | None = None
    rules: list[ProcessExceptionRule] = Field(default_factory=list)


DEFAULT_SETTLEMENT_EXCEPTION_CATALOG = ProcessExceptionCatalog(
    process_key="settlement",
    canonical_aggregate_type=CANONICAL_SETTLEMENT_AGGREGATE,
    canonical_process_definition_key=CANONICAL_SETTLEMENT_PROCESS_DEFINITION_KEY,
    rules=[
        ProcessExceptionRule(
            rule_id="settlement.quality.deviation",
            category="quality-deviation",
            trigger_key="quality_outside_tolerance",
            decision_mode="workflow-approval",
            requires_approval=True,
            approver_roles=["qs", "annahme_leiter"],
            description="Qualitätswerte liegen außerhalb des zulässigen Bereichs.",
        ),
        ProcessExceptionRule(
            rule_id="settlement.deduction.manual",
            category="deduction",
            trigger_key="manual_deduction_requested",
            decision_mode="manual-approval",
            requires_approval=True,
            approver_roles=["fibu", "leitung"],
            description="Manueller Abzug außerhalb automatisch berechneter Regeln.",
        ),
        ProcessExceptionRule(
            rule_id="settlement.complaint.open",
            category="complaint",
            trigger_key="complaint_open",
            decision_mode="policy",
            policy_rule_id="complaint.open",
            requires_approval=True,
            approver_roles=["qs", "vertrieb"],
            description="Offene Reklamation blockiert automatische Verarbeitung.",
        ),
    ],
)
