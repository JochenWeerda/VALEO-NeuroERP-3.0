"""Chart of Accounts Gateway Endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from finance_shared.auth import FiBuPermission

from app.api.utils import build_response
from app.clients.base import GatewayServiceError
from app.dependencies import get_access_policy, get_master_data_client, get_tenant

router = APIRouter()


@router.get("/chart-of-accounts")
async def list_chart_of_accounts(
    tenant: str = Depends(get_tenant),
    master_data_client=Depends(get_master_data_client),
    policy=Depends(get_access_policy),
):
    policy.ensure_permission(FiBuPermission.MASTER_DATA_READ)
    try:
        items = await master_data_client.list_chart_of_accounts(tenant)
        return build_response({"items": items}, source="fibu-master-data", meta={"count": len(items)})
    except GatewayServiceError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=exc.detail) from exc

