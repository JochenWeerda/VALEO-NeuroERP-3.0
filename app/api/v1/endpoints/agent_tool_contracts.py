"""
External agent tool contracts.

Provides a stable contract/manifest surface for external agents and tool
generators based on the productive Process-Kernel MCP registry.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.core.agent_tool_contract_manifest import build_agent_tool_contract_manifest

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut
from app.api.v1.schemas.agent_tool_contracts_schemas import AgentToolContractsOut


router = APIRouter(prefix="/agent/tool-contracts", tags=["agents", "mcp", "openapi"])


@router.get("", summary="External Agent Tool Contract Manifest",
    response_model=AgentToolContractsOut
)
def get_agent_tool_contract_manifest(
    domain: str | None = Query(default=None, description="Optional domain filter"),
    tool_name: str | None = Query(default=None, description="Optional tool name filter"),
) -> dict:
    manifest = build_agent_tool_contract_manifest(domain=domain, tool_name=tool_name)
    return manifest.model_dump()


@router.get("/mcp", summary="MCP Tool Definitions",
    response_model=AgentToolContractsOut
)
def get_mcp_tool_definitions(
    domain: str | None = Query(default=None, description="Optional domain filter"),
    tool_name: str | None = Query(default=None, description="Optional tool name filter"),
) -> dict:
    manifest = build_agent_tool_contract_manifest(domain=domain, tool_name=tool_name)
    return {
        "schema_version": manifest.schema_version,
        "generated_at": manifest.generated_at,
        "tool_count": manifest.tool_count,
        "domains": manifest.domains,
        "auth_schemes": manifest.auth_schemes,
        "tools": [tool.mcp_definition for tool in manifest.tools],
        "tool_views": [tool.model_dump() for tool in manifest.tools],
    }


@router.get("/openapi", summary="OpenAPI-linked Tool Contracts",
    response_model=AgentToolContractsOut
)
def get_openapi_tool_contracts(
    domain: str | None = Query(default=None, description="Optional domain filter"),
) -> dict:
    manifest = build_agent_tool_contract_manifest(domain=domain)
    return {
        "schema_version": manifest.schema_version,
        "generated_at": manifest.generated_at,
        "openapi_url": manifest.openapi_url,
        "tool_count": manifest.tool_count,
        "domains": manifest.domains,
        "auth_schemes": manifest.auth_schemes,
        "tools": [
            {
                "tool_name": tool.tool_name,
                "method": tool.method,
                "path": tool.path,
                "operation_id": tool.openapi_ref.operation_id,
                "openapi_url": tool.openapi_ref.openapi_url,
                "required_headers": tool.required_headers,
                "required_parameters": tool.required_parameters,
                "optional_parameters": tool.optional_parameters,
            }
            for tool in manifest.tools
        ],
        "tool_views": [tool.model_dump() for tool in manifest.tools],
    }


@router.get("/{tool_name}", summary="Single Tool Contract",
    response_model=AgentToolContractsOut
)
def get_agent_tool_contract(tool_name: str) -> dict:
    manifest = build_agent_tool_contract_manifest(tool_name=tool_name)
    if not manifest.tools:
        raise HTTPException(status_code=404, detail=f"Tool contract {tool_name!r} not found")
    return manifest.tools[0].model_dump()
