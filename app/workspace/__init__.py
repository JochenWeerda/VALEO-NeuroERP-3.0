"""Adaptive Workspace: Fachaktionen-Katalog, Alias-Resolver, Event-Mapping.

Kein eigener Schreibpfad. Writes bleiben bei den vorhandenen Domain-Commands
und MCP-Adaptern (MCP-WRITE-001 bis 015).
"""

from app.workspace.events import (
    CANONICAL_EVENTS,
    IST_TO_SOLL,
    canonical_event,
    mirror_ist_event_to_workspace,
    project_workspace_event,
    publish_workspace_sse,
    resolve_ist_event_type,
)
from app.workspace.fachaktionen import (
    Resolution,
    WorkspaceFachaktionenError,
    execute_mcp,
    list_catalog,
    load_catalog,
    resolve_command,
)

__all__ = [
    "CANONICAL_EVENTS",
    "IST_TO_SOLL",
    "Resolution",
    "WorkspaceFachaktionenError",
    "canonical_event",
    "execute_mcp",
    "mirror_ist_event_to_workspace",
    "publish_workspace_sse",
    "resolve_ist_event_type",
    "list_catalog",
    "load_catalog",
    "project_workspace_event",
    "resolve_command",
]
