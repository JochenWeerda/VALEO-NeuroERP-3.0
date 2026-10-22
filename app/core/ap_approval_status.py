from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.core.explainability import ExplainabilityDetail, ExplainabilityView, build_policy_explainability_view
from app.core.policy_decisions import PolicyOverrideResolution


class ApprovalStatusResponse(BaseModel):
    invoice_id: str
    status: str
    required_approvals: int
    current_approvals: int
    approvals: list[dict[str, Any]]
    rejections: list[dict[str, Any]]
    applicable_rule: dict[str, Any] | None
    can_post: bool
    can_pay: bool
    override_resolution: PolicyOverrideResolution
    explainability: ExplainabilityView


APPROVAL_STATUS_TO_INSTANCE_STATUS = {
    "not_requested": "running",
    "pending": "waiting",
    "partially_approved": "waiting",
    "approved": "completed",
    "rejected": "failed",
}

APPROVAL_STATUS_TO_DOCUMENT_STATUS = {
    "not_requested": "ENTWURF",
    "pending": "ZUR_FREIGABE",
    "partially_approved": "TEILWEISE_FREIGEGEBEN",
    "approved": "FREIGEGEBEN",
    "rejected": "ABGELEHNT",
}

DOCUMENT_STATUS_TO_APPROVAL_STATUS = {
    "ENTWURF": "not_requested",
    "ZUR_FREIGABE": "pending",
    "TEILWEISE_FREIGEGEBEN": "partially_approved",
    "FREIGEGEBEN": "approved",
    "VERBUCHT": "approved",
    "BEZAHLT": "approved",
    "ABGELEHNT": "rejected",
}


def build_approval_override_resolution(
    invoice_id: str,
    tenant_id: str,
    applicable_rule: dict[str, Any] | None,
) -> PolicyOverrideResolution:
    rule_id = "ap.approval.default"
    effective_scope = "global"
    effective_scope_key = "approval-default"
    applied_reason = "Keine spezielle Freigaberegel aktiv."

    if applicable_rule is not None:
        rule_id = str(applicable_rule.get("id") or "ap.approval.rule")
        effective_scope = "tenant"
        effective_scope_key = tenant_id
        applied_reason = f"Freigaberegel {applicable_rule.get('name') or rule_id} angewendet."

    return PolicyOverrideResolution(
        rule_id=rule_id,
        effective_scope=effective_scope,
        effective_scope_key=effective_scope_key,
        effective_enabled=True,
        effective_params={
            "invoice_id": invoice_id,
            "required_approvals": int(applicable_rule.get("required_approvals", 1))
            if applicable_rule is not None
            else 1,
            "approval_roles": list(applicable_rule.get("approval_roles", []))
            if applicable_rule is not None
            else [],
        },
        applied_reason=applied_reason,
        applied_source="ap-approval-workflow",
    )


def build_approval_explainability(
    *,
    status: str,
    resolution: PolicyOverrideResolution,
    current_approvals: int,
    required_approvals: int,
    approvals: list[dict[str, Any]],
    rejections: list[dict[str, Any]],
) -> ExplainabilityView:
    explainability = build_policy_explainability_view(
        resolution,
        blocked=status == "rejected",
        needs_approval=status in {"pending", "partially_approved"},
    )

    if status == "approved":
        explainability.summary = "Rechnung ist freigegeben."
    elif status == "not_requested":
        explainability.summary = "Fuer diese Rechnung wurde noch keine Freigabe angefordert."
    elif status == "rejected":
        explainability.summary = "Rechnung wurde im Freigabeworkflow abgelehnt."

    explainability.details.extend(
        [
            ExplainabilityDetail(label="Status", value=status),
            ExplainabilityDetail(label="Freigaben", value=f"{current_approvals}/{required_approvals}"),
        ]
    )
    if approvals:
        explainability.details.append(
            ExplainabilityDetail(
                label="Freigegeben von",
                value=", ".join(str(item.get("approved_by")) for item in approvals if item.get("approved_by")),
            )
        )
    if rejections:
        explainability.details.append(
            ExplainabilityDetail(
                label="Abgelehnt von",
                value=", ".join(str(item.get("approved_by")) for item in rejections if item.get("approved_by")),
            )
        )
    return explainability


def build_approval_status_response(
    *,
    invoice_id: str,
    tenant_id: str,
    status: str,
    required_approvals: int,
    approvals: list[dict[str, Any]],
    rejections: list[dict[str, Any]],
    applicable_rule: dict[str, Any] | None,
) -> ApprovalStatusResponse:
    resolution = build_approval_override_resolution(invoice_id, tenant_id, applicable_rule)
    explainability = build_approval_explainability(
        status=status,
        resolution=resolution,
        current_approvals=len(approvals),
        required_approvals=required_approvals,
        approvals=approvals,
        rejections=rejections,
    )
    return ApprovalStatusResponse(
        invoice_id=invoice_id,
        status=status,
        required_approvals=required_approvals,
        current_approvals=len(approvals),
        approvals=approvals,
        rejections=rejections,
        applicable_rule=applicable_rule,
        can_post=(status == "approved"),
        can_pay=(status == "approved"),
        override_resolution=resolution,
        explainability=explainability,
    )
