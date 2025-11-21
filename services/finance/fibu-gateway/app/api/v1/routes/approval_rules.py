"""Endpoints zur Verwaltung der FiBu-Approval-Rules pro Tenant."""

from __future__ import annotations

from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from finance_shared.auth import FiBuRole
from pydantic import BaseModel, Field

from app.api.utils import build_response
from app.dependencies import get_approval_rule_store, get_tenant
from app.storage.approval_rules import ApprovalRuleRecord, ApprovalRuleStore

router = APIRouter()


class ApprovalRulePayload(BaseModel):
    tenant_id: str = Field(min_length=1)
    currency: str = Field(..., min_length=3, max_length=3)
    min_amount: Decimal = Field(gt=0)
    required_role: FiBuRole


class ApprovalRuleResponse(BaseModel):
    tenant_id: str
    currency: str
    min_amount: Decimal
    required_role: FiBuRole

    @classmethod
    def from_record(cls, record: ApprovalRuleRecord) -> "ApprovalRuleResponse":
        return cls(
            tenant_id=record.tenant_id,
            currency=record.currency,
            min_amount=record.min_amount,
            required_role=record.required_role,
        )


@router.get("/approval-rules")
async def list_approval_rules(
    tenant: str = Depends(get_tenant),
    store: ApprovalRuleStore = Depends(get_approval_rule_store),
):
    records = store.list_rules(tenant)
    data = {
        "items": [ApprovalRuleResponse.from_record(record).model_dump() for record in records],
        "tenant": tenant,
    }
    return build_response(data, source="fibu-gateway", meta={"count": len(records)})


@router.post("/approval-rules", status_code=status.HTTP_201_CREATED)
async def upsert_approval_rule(
    payload: ApprovalRulePayload,
    store: ApprovalRuleStore = Depends(get_approval_rule_store),
):
    try:
        store.upsert_rule(
            tenant_id=payload.tenant_id,
            currency=payload.currency,
            min_amount=payload.min_amount,
            required_role=payload.required_role,
        )
        data = {
            "tenant_id": payload.tenant_id,
            "currency": payload.currency.upper(),
            "min_amount": payload.min_amount,
            "required_role": payload.required_role,
        }
        return build_response(data, source="fibu-gateway")
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


