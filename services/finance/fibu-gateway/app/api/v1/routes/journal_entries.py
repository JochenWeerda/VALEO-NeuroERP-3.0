"""Journal Entry Gateway Endpoints."""

from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from finance_shared.auth import FiBuPermission

from app.api.utils import build_response
from app.clients.base import GatewayServiceError
from app.dependencies import (
    get_access_policy,
    get_audit_trail,
    get_core_client,
    get_event_publisher,
    get_tenant,
)

router = APIRouter()


@router.get("/journal-entries")
async def list_journal_entries(
    tenant: str = Depends(get_tenant),
    core_client=Depends(get_core_client),
    policy=Depends(get_access_policy),
):
    policy.ensure_permission(FiBuPermission.JOURNAL_READ)
    try:
        items = await core_client.list_journal_entries(tenant)
        return build_response({"items": items}, source="fibu-core", meta={"count": len(items)})
    except GatewayServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=exc.detail) from exc


@router.post("/journal-entries", status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    payload: dict,
    tenant: str = Depends(get_tenant),
    core_client=Depends(get_core_client),
    policy=Depends(get_access_policy),
    audit_trail=Depends(get_audit_trail),
    publisher=Depends(get_event_publisher),
):
    try:
        policy.ensure_permission(FiBuPermission.JOURNAL_CREATE)
        amount = Decimal(str(payload.get("amount", "0")))
        currency = payload.get("currency", "EUR")
        if policy.require_approval(amount=amount, currency=currency):
            policy.ensure_permission(FiBuPermission.JOURNAL_APPROVE)

        journal = await core_client.create_journal_entry(tenant, payload)
        entry = audit_trail.create_entry(
            entity_type="journal_entry",
            entity_id=str(journal.get("id", payload.get("id", "unknown"))),
            action="create",
            payload=journal,
            user_id=policy.user_id,
        )
        audit_trail.append_entry(entry)
        await publisher.publish_booking_created(
            tenant_id=tenant,
            booking_id=journal.get("id"),
            account_id=journal.get("account_id", payload.get("account_id", "")),
            amount=amount,
            currency=currency,
            period=journal.get("period", payload.get("period", "")),
            document_id=journal.get("document_id"),
            approved=journal.get("approved", False),
        )
        return build_response(journal, source="fibu-core")
    except GatewayServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=exc.detail) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

