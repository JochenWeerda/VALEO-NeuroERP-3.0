"""
Shared policy override and explainability models for the process kernel.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


PolicyOverrideScope = Literal["global", "tenant", "role", "process"]

POLICY_OVERRIDE_PRIORITY: dict[PolicyOverrideScope, int] = {
    "global": 10,
    "tenant": 20,
    "role": 30,
    "process": 40,
}


class PolicyOverrideLayer(BaseModel):
    scope: PolicyOverrideScope
    scope_key: str = Field(min_length=1)
    rule_id: str = Field(min_length=1)
    enabled: bool | None = None
    reason: str = Field(min_length=1)
    params_override: dict[str, Any] = Field(default_factory=dict)
    valid_until: datetime | None = None
    source: str = Field(default="manual", min_length=1)


class PolicyOverrideResolution(BaseModel):
    rule_id: str = Field(min_length=1)
    effective_scope: PolicyOverrideScope | None = None
    effective_scope_key: str | None = None
    effective_enabled: bool | None = None
    effective_params: dict[str, Any] = Field(default_factory=dict)
    applied_reason: str | None = None
    applied_source: str | None = None
    evaluated_layers: list[PolicyOverrideLayer] = Field(default_factory=list)


def resolve_policy_override_layers(
    rule_id: str,
    layers: list[PolicyOverrideLayer],
    *,
    base_params: dict[str, Any] | None = None,
) -> PolicyOverrideResolution:
    relevant = [layer for layer in layers if layer.rule_id == rule_id]
    relevant.sort(key=lambda layer: POLICY_OVERRIDE_PRIORITY[layer.scope])

    resolution = PolicyOverrideResolution(rule_id=rule_id, effective_params=dict(base_params or {}))
    for layer in relevant:
        resolution.evaluated_layers.append(layer)
        resolution.effective_scope = layer.scope
        resolution.effective_scope_key = layer.scope_key
        resolution.applied_reason = layer.reason
        resolution.applied_source = layer.source
        if layer.enabled is not None:
            resolution.effective_enabled = layer.enabled
        if layer.params_override:
            resolution.effective_params = {**resolution.effective_params, **layer.params_override}
    return resolution
