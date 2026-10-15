"""Versioned public command inputs; identities and approvals are server-owned."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, StrictInt
from modules.agrar.contracts.harvest_deductions_v1 import HarvestDeductionTermsV1


class CommandIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    idempotency_key: UUID


class RuleCreateIn(CommandIn):
    rule_id: str = Field(min_length=1, max_length=100, pattern=r"^[\w.:-]+$")
    expected_version: StrictInt = Field(ge=0)
    terms: HarvestDeductionTermsV1


class RuleDecisionIn(CommandIn):
    expected_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    reason: str = Field(min_length=3, max_length=2000)
    expires_at: datetime | None = None


class ContextCommandIn(CommandIn):
    expected_context_hash: str = Field(pattern=r"^[a-f0-9]{64}$")


class RuleBindIn(ContextCommandIn):
    rule_version_id: UUID


class MeasurementAttestIn(ContextCommandIn):
    protocol_id: str = Field(min_length=1, max_length=100)
    expected_protocol_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    measurement_method: str = Field(min_length=1, max_length=100)
    measurement_method_version: str = Field(min_length=1, max_length=100)
    source_reference: str = Field(min_length=1, max_length=255)


class CalculationApproveIn(CommandIn):
    expected_calculation_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    expires_at: datetime
    reason: str = Field(min_length=3, max_length=2000)
    acknowledge_quality_exception: bool = False


class FinancialReleaseIn(CommandIn):
    expected_calculation_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
