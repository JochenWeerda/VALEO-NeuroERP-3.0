"""Input contracts for generic NeuroASSIST capability runs."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field
from app.core.tenant_context import get_current_tenant_id


class BestellvorschlagRunInput(BaseModel):
    tenant_id: str = Field(default_factory=get_current_tenant_id, min_length=1)


class FinanceSkontoRunInput(BaseModel):
    available_cash: Decimal = Field(gt=0)
    payment_date: datetime | None = None


class ComplianceCopilotRunInput(BaseModel):
    entity_type: str = Field(min_length=3)
    entity_id: str = Field(min_length=1)
    entity_data: dict[str, Any] = Field(default_factory=dict)


class DataQualityAssistantRunInput(BaseModel):
    entity_type: str = Field(min_length=3)
    payload_snapshot: dict[str, Any] = Field(default_factory=dict)
    dq_findings: list[dict[str, Any]] = Field(default_factory=list)
    ingestion_context: dict[str, Any] = Field(default_factory=dict)


class OperationsExceptionRunInput(BaseModel):
    process_definition_key: str = Field(min_length=3)
    exception_code: str = Field(min_length=3)
    exception_context: dict[str, Any] = Field(default_factory=dict)
    aggregate_type: str | None = Field(default=None, min_length=1)
    aggregate_id: str | None = Field(default=None, min_length=1)
    evidence_refs: list[str] = Field(default_factory=list)


def validate_capability_input(
    capability_key: str,
    *,
    tenant_id: str | None = None,
    parameters: dict[str, Any] | None = None,
) -> BaseModel:
    tenant_id = tenant_id or get_current_tenant_id()
    payload = dict(parameters or {})
    if capability_key == "bestellvorschlag_assistant":
        return BestellvorschlagRunInput(tenant_id=tenant_id)
    if capability_key == "finance_skonto_assistant":
        return FinanceSkontoRunInput.model_validate(payload)
    if capability_key == "compliance_copilot":
        return ComplianceCopilotRunInput.model_validate(payload)
    if capability_key == "data_quality_assistant":
        return DataQualityAssistantRunInput.model_validate(payload)
    if capability_key == "operations_exception_assistant":
        return OperationsExceptionRunInput.model_validate(payload)
    raise KeyError(f"Unknown NeuroASSIST capability input contract: {capability_key}")
