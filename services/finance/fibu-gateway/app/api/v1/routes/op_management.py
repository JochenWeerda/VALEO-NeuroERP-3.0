"""Open Item Management."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from finance_shared.auth import FiBuPermission

from app.api.utils import build_response
from app.clients.base import GatewayServiceError
from app.dependencies import get_access_policy, get_op_client, get_tenant

router = APIRouter()


@router.get("/op/debtor-open-items")
async def list_debtor_open_items(
    debtor: str | None = Query(default=None),
    tenant: str = Depends(get_tenant),
    op_client=Depends(get_op_client),
    policy=Depends(get_access_policy),
):
    policy.ensure_permission(FiBuPermission.OP_READ)
    try:
        items = await op_client.list_open_items(tenant, debtor)
        meta = {"count": len(items)}
        if debtor:
            meta["filter"] = {"debtor": debtor}
        return build_response({"items": items}, source="fibu-op", meta=meta)
    except GatewayServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=exc.detail) from exc

