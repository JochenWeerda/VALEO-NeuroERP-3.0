"""MCP-ERP-TOOLS-001 — API fuer den ERP-Tool-Katalog."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.services.mcp_tool_registry_service import mcp_tool_registry_service

router = APIRouter(prefix="/mcp/tools", tags=["mcp", "tools"])


@router.get(
    "",
    summary="ERP-MCP-Toolkatalog listen",
    response_model=list[dict[str, Any]],
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
    response_model=dict[str, Any],
)
async def get_summary() -> dict[str, Any]:
    return mcp_tool_registry_service.summary()


@router.get(
    "/{tool_id}",
    summary="Einzelnes MCP-Tool abrufen",
    response_model=dict[str, Any],
)
async def get_tool(tool_id: str) -> dict[str, Any]:
    try:
        return mcp_tool_registry_service.get_tool(tool_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Tool not found: {tool_id}") from exc
