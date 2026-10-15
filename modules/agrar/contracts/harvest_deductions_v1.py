"""Immutable input contract for a trusted impurity-rule resolver.

Not an HTTP input or a grant of approval: production must resolve these records
from its authoritative version store. Studio supplies explicitly synthetic data.
"""
from datetime import date
from decimal import Decimal, localcontext
from hashlib import sha256
import json
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator, model_validator


class HarvestDeductionRuleV1(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["harvest.deductions.v1"] = "harvest.deductions.v1"
    rule_id: str = Field(min_length=1, max_length=100)
    rule_version: StrictInt = Field(ge=1)
    tenant_id: str = Field(min_length=1, max_length=100)
    contract_id: str | None = Field(default=None, min_length=1, max_length=100)
    customer_id: str = Field(min_length=1, max_length=100)
    article_id: str = Field(min_length=1, max_length=100)
    valid_from: date
    valid_until: date
    source_reference: str = Field(min_length=1, max_length=255)
    measurement_method: str = Field(min_length=1, max_length=100)
    measurement_method_version: str = Field(min_length=1, max_length=100)
    impurities_free_pct: Decimal = Field(ge=0, le=100, allow_inf_nan=False)
    quality_limit_pct: Decimal | None = Field(default=None, ge=0, le=100, allow_inf_nan=False)
    windage_mode: Literal["informative"] = "informative"
    deduction_basis: Literal["delivered_quantity_kg"] = "delivered_quantity_kg"
    quantity_rounding: Literal["0.001_HALF_UP"] = "0.001_HALF_UP"

    @field_validator("impurities_free_pct", "quality_limit_pct")
    @classmethod
    def normalized_percentage(cls, value):
        if value is None:
            return None
        if value == 0:
            return Decimal("0")
        # Canonical hashes must not round the agreed terms at Decimal's default precision.
        with localcontext() as context:
            context.prec = max(context.prec, len(value.as_tuple().digits))
            return value.normalize()

    @model_validator(mode="after")
    def ordered_validity(self):
        if self.valid_until < self.valid_from:
            raise ValueError("Vertragsregel hat einen ungueltigen Geltungszeitraum.")
        return self

    @property
    def content_hash(self) -> str:
        content = json.dumps(self.model_dump(mode="json"), sort_keys=True,
                             separators=(",", ":"), allow_nan=False)
        return sha256(content.encode()).hexdigest()

    def require_scope(self, *, tenant_id: str, contract_id: str | None,
                      customer_id: str, article_id: str, delivery_date: date) -> None:
        if ((self.tenant_id, self.contract_id, self.customer_id, self.article_id)
                != (tenant_id, contract_id, customer_id, article_id)
                or type(delivery_date) is not date
                or not self.valid_from <= delivery_date <= self.valid_until):
            raise ValueError("Vertragsregel passt nicht zu Mandant, Vertrag, Partner, Artikel oder Lieferdatum.")


class HarvestRuleResolver(Protocol):
    def __call__(self, *, tenant_id: str, acceptance_id: str) -> HarvestDeductionRuleV1: ...
