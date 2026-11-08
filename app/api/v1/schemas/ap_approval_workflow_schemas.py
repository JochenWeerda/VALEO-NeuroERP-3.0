"""Versioned AP review inputs; actors are always supplied by authentication."""
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator, field_validator

from app.auth.finance_roles import FINANCE_APPROVAL_ROLES


class ApprovalRuleCondition(BaseModel):
    field: Literal["amount", "material_group", "supplier_id"]
    operator: Literal["gt", "gte", "lt", "lte", "eq", "in"]
    value: Any

    @model_validator(mode="after")
    def supported_value(self):
        values = self.value if self.operator == "in" else [self.value]
        if not isinstance(values, list) or not 1 <= len(values) <= 100:
            raise ValueError("Condition requires a bounded nonempty list")
        if self.field == "amount":
            try:
                numbers = [Decimal(str(value)) for value in values]
                if any(not number.is_finite() or number < 0 for number in numbers):
                    raise ValueError("Invalid amount condition")
            except (InvalidOperation, TypeError, ValueError):
                raise ValueError("Invalid amount condition") from None
        elif self.operator not in {"eq", "in"} or any(
            not isinstance(value, str) or not value.strip() or len(value) > 200 for value in values
        ):
            raise ValueError("Text condition requires eq/in and nonempty strings")
        return self


class ApprovalRuleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    conditions: list[ApprovalRuleCondition] = Field(min_length=1, max_length=50)
    required_approvals: int = Field(ge=1, le=4)
    approval_roles: list[str] = Field(min_length=1, max_length=len(FINANCE_APPROVAL_ROLES))
    priority: int = 0
    active: bool = True

    @field_validator("approval_roles")
    @classmethod
    def declared_roles(cls, values):
        if len(set(values)) != len(values) or not set(values).issubset(FINANCE_APPROVAL_ROLES):
            raise ValueError("Use existing finance approval roles")
        return values


class ApprovalRuleResponse(BaseModel):
    id: str
    name: str
    description: str | None
    conditions: list[dict[str, Any]]
    required_approvals: int
    approval_roles: list[str]
    priority: int
    active: bool
    created_at: datetime
    updated_at: datetime


class ApprovalRequest(BaseModel):
    invoice_id: str = Field(min_length=1, max_length=64)
    requested_by: str | None = Field(default=None, deprecated=True, description="Ignored; verified token subject is used")
    comment: str | None = Field(default=None, max_length=2000)


class ApprovalDecisionReference(BaseModel):
    approval_request_id: str = Field(min_length=1, max_length=64)
    comment: str | None = Field(default=None, max_length=2000)


class ApprovalAction(ApprovalDecisionReference):
    invoice_id: str = Field(min_length=1, max_length=64)
    approved_by: str | None = Field(default=None, deprecated=True, description="Ignored; verified token subject is used")
    action: Literal["approve", "reject"]
