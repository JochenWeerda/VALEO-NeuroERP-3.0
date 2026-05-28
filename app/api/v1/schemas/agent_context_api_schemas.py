"""Auto-generated domain schemas for agent context api.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class AgentContextApiOut(BaseSchema):
    """Response schema for agent context api endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class AgentContextCreateRequest(BaseModel):
    agent_id: str
    tenant_id: str
    delegated_roles: list[str]
    ttl_sekunden: int = 3600


class AgentDispatchRequest(BaseModel):
    command_name: str
    resource_tenant_id: str
    resource_type: str = "agent_command"
    issuer_role: str = "agent"


class AgentKnowledgePackRequest(BaseModel):
    rolle: str
    kanal: str = "CHAT"
    capability_key: Optional[str] = None
    query: str = ""
    limit: int = 4

