"""MCP-ERP-TOOLS-001 — API fuer den ERP-Tool-Katalog."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session
from app.auth.deps_oidc import get_current_user
from app.core.database import get_db
from app.services.mcp_execution_service import ToolExecutionRequest, execute_mcp_tool

from app.services.mcp_tool_registry_service import mcp_tool_registry_service
from app.api.v1.schemas.base import TypedObjectOut

router = APIRouter(prefix="/mcp/tools", tags=["mcp", "tools"])


@router.post("/call", response_model=TypedObjectOut, summary="Authenticated ERP tool execution")
def call_tool(
    body: ToolExecutionRequest,
    user: dict = Depends(get_current_user),
    tenant_header: str | None = Header(default=None, alias="X-Tenant-ID"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return execute_mcp_tool(db, body, user, tenant_header)


@router.get(
    "",
    summary="ERP-MCP-Toolkatalog listen",
    response_model=list[TypedObjectOut],
)
async def list_tools(
    domain: str | None = Query(default=None),
    scope: str | None = Query(default=None),
    risk_class: str | None = Query(default=None),
) -> list[dict[str, Any]]:
    return mcp_tool_registry_service.list_tools(
        domain=domain,
        scope=scope,
        risk_class=risk_class,
    )


@router.get(
    "/summary",
    summary="Tool-Katalog Zusammenfassung",
    response_model=TypedObjectOut,
)
async def get_summary() -> dict[str, Any]:
    return mcp_tool_registry_service.summary()


@router.get(
    "/{tool_id}",
    summary="Einzelnes MCP-Tool abrufen",
    response_model=TypedObjectOut,
)
async def get_tool(tool_id: str) -> dict[str, Any]:
    try:
        return mcp_tool_registry_service.get_tool(tool_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Tool not found: {tool_id}") from exc
