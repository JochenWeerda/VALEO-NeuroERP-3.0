"""
External Agent Tool Contract manifest.

This module combines the productive Process-Kernel MCP registry with
OpenAPI- and tenant/auth metadata so external agents can consume one
stable, machine-readable contract surface.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from app.core.agent_command_manifest import build_agent_command_manifest
from app.core.mcp_tool_contracts import MCPToolContract, MCPToolRegistry, get_process_kernel_mcp_tools


class AgentToolContractSource(BaseModel):
    rel: str
    href: str
    description: str


class AgentToolContractOpenAPIRef(BaseModel):
    method: str
    path: str
    openapi_url: str = "/api/v1/openapi.json"
    operation_id: str


class AgentToolContractEntry(BaseModel):
    tool_name: str
    domain: str
    operation: str
    description: str
    category: str
    method: str
    path: str
    requires_approval: bool
    idempotent: bool
    tenant_scoped: bool = True
    auth_scheme: str = "bearer"
    required_headers: list[str] = Field(default_factory=lambda: ["Authorization", "X-Tenant-ID"])
    required_parameters: list[str] = Field(default_factory=list)
    optional_parameters: list[str] = Field(default_factory=list)
    mcp_definition: dict[str, Any]
    openapi_ref: AgentToolContractOpenAPIRef
    api_endpoint: str
    schema_version: int = 1


class AgentToolContractManifest(BaseModel):
    schema_version: int = 1
    generated_at: str
    manifest_kind: str = "MCP_OPENAPI_TOOL_CONTRACT"
    sources: list[AgentToolContractSource]
    openapi_url: str = "/api/v1/openapi.json"
    agent_command_manifest_url: str = "/api/v1/commands/agent-manifest"
    mcp_registry_url: str = "/api/v1/process/agent/tool-registry"
    tool_count: int
    domains: list[str]
    auth_schemes: list[str]
    approval_required_count: int
    idempotent_count: int
    command_manifest: dict[str, Any]
    tools: list[AgentToolContractEntry]
    notes: list[str] = Field(default_factory=list)


def _split_endpoint(api_endpoint: str) -> tuple[str, str]:
    parts = api_endpoint.strip().split(" ", 1)
    if len(parts) == 2:
        return parts[0].upper(), parts[1].strip()
    return "GET", api_endpoint.strip()


def _build_entry(contract: MCPToolContract) -> AgentToolContractEntry:
    method, path = _split_endpoint(contract.api_endpoint or "GET /api/v1/unknown")
    required_headers = ["Authorization", "X-Tenant-ID"]
    if method not in {"GET", "HEAD"}:
        required_headers.append("Content-Type")
    return AgentToolContractEntry(
        tool_name=contract.tool_name,
        domain=contract.domain,
        operation=contract.operation,
        description=contract.beschreibung,
        category=contract.kategorie.value,
        method=method,
        path=path,
        requires_approval=contract.requires_approval,
        idempotent=contract.kategorie.value in {"LESEN", "BERECHNEN", "VALIDIEREN"},
        tenant_scoped=True,
        required_headers=required_headers,
        required_parameters=[p.name for p in contract.pflicht_parameter],
        optional_parameters=[p.name for p in contract.optionale_parameter],
        mcp_definition=contract.as_mcp_tool(),
        openapi_ref=AgentToolContractOpenAPIRef(
            method=method,
            path=path,
            operation_id=contract.tool_name,
        ),
        api_endpoint=contract.api_endpoint or f"{method} {path}",
    )


def build_agent_tool_contract_manifest(
    domain: str | None = None,
    tool_name: str | None = None,
) -> AgentToolContractManifest:
    registry: MCPToolRegistry = get_process_kernel_mcp_tools()
    tools = registry.tools

    if domain:
        tools = [tool for tool in tools if tool.domain == domain]
    if tool_name:
        tools = [tool for tool in tools if tool.tool_name == tool_name]

    entries = [_build_entry(tool) for tool in tools]
    command_manifest = build_agent_command_manifest()

    return AgentToolContractManifest(
        generated_at=datetime.now(timezone.utc).isoformat(),
        sources=[
            AgentToolContractSource(
                rel="openapi",
                href="/api/v1/openapi.json",
                description="OpenAPI 3.x source for code generation and agent tool binding",
            ),
            AgentToolContractSource(
                rel="mcp-registry",
                href="/api/v1/process/agent/tool-registry",
                description="Process-Kernel MCP tool registry",
            ),
            AgentToolContractSource(
                rel="agent-command-manifest",
                href="/api/v1/commands/agent-manifest",
                description="Agent command manifest for idempotent business commands",
            ),
        ],
        tool_count=len(entries),
        domains=sorted({tool.domain for tool in entries}),
        auth_schemes=sorted({tool.auth_scheme for tool in entries}),
        approval_required_count=sum(1 for tool in entries if tool.requires_approval),
        idempotent_count=sum(1 for tool in entries if tool.idempotent),
        command_manifest={
            "schema_version": command_manifest.schema_version,
            "command_count": len(command_manifest.commands),
            "agent_restricted_commands": command_manifest.agent_restricted_commands,
            "fully_blocked_for_agents": command_manifest.fully_blocked_for_agents,
        },
        tools=entries,
        notes=[
            "OpenAPI is the canonical source for request/response schemas.",
            "MCP tool definitions are provided for agent runtimes that prefer tool manifests.",
            "Business commands and MCP tools are related but separate contract layers.",
        ],
    )
