"""
Agent Command Manifest — Wave 5 Paket A.

Oeffentliches Manifest aller Commands, die von Agenten aufgerufen werden koennen.
"""

from __future__ import annotations

from pydantic import BaseModel

from app.core.business_commands import CommandDefinition, build_core_command_catalog


class AgentCommandEntry(BaseModel):
    """Ein Command-Eintrag im Agent-Manifest."""
    command_name: str
    aggregate_type: str
    allowed_agent_types: list[str]
    requires_human_confirmation: bool
    idempotent: bool
    post_event: str | None
    schema_version: int = 1


class AgentCommandManifest(BaseModel):
    """Oeffentliches Manifest aller Commands, die von Agenten aufgerufen werden koennen."""
    commands: list[AgentCommandEntry]
    agent_restricted_commands: list[str]    # Commands mit requires_human_confirmation
    fully_blocked_for_agents: list[str]     # Commands mit leerem allowed_agent_types
    schema_version: int = 1


def build_agent_command_manifest(
    catalog: list[CommandDefinition] | None = None,
) -> AgentCommandManifest:
    if catalog is None:
        catalog = build_core_command_catalog()
    entries = [
        AgentCommandEntry(
            command_name=cd.command_name,
            aggregate_type=cd.aggregate_type,
            allowed_agent_types=cd.allowed_agent_types,
            requires_human_confirmation=cd.requires_human_confirmation,
            idempotent=cd.idempotent,
            post_event=cd.post_event,
        )
        for cd in catalog
    ]
    restricted = [e.command_name for e in entries if e.requires_human_confirmation]
    blocked = [e.command_name for e in entries if not e.allowed_agent_types]
    return AgentCommandManifest(
        commands=entries,
        agent_restricted_commands=restricted,
        fully_blocked_for_agents=blocked,
    )
