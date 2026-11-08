"""Freigabe generischer Agenten-Schreibwege (MCP ``mask.action.execute`` und Kommandowege mit Agentenpruefung).

Zwei Phasen, gewaehlt in ``config/mcp_erp_tools.yaml`` am Werkzeug ``mask.action.execute``:

``agent_write_phase: entwicklung``
    Nutzerentscheidung 08.11.2026: Waehrend der Softwareerstellung sind alle MCP- und CLI-Schreibzugriffe
    freigegeben. Jeder deklarierte Kommandoweg ist fuer Agenten mit ``masks:write`` offen; Rechte, Mandant,
    Audit und Wiederholungsschutz prueft weiter der Ziel-Endpunkt. Fachregeln der Maske (``forbiddenForAgents``,
    ``humanApprovalRequired``, Belegadapter) bleiben unberuehrt.
sonst (Produktivbetrieb)
    Nur ausdruecklich je Aktion freigegebene ``write_capabilities``; alles andere scheitert geschlossen.
    Vor dem Go-Live den Schalter entfernen.

Ist die Registry nicht lesbar, gilt der Produktivbetrieb (geschlossen).
"""
from fastapi import HTTPException
import yaml

DEVELOPMENT_PHASE = "entwicklung"


def _registry() -> dict:
    from app.services.mcp_tool_registry_service import mcp_tool_registry_service
    try:
        registry = mcp_tool_registry_service.get_tool("mask.action.execute")
    except (KeyError, TypeError, AttributeError, OSError, ValueError, yaml.YAMLError):
        return {}
    return registry if isinstance(registry, dict) else {}


def development_release() -> bool:
    """Sind waehrend der Entwicklung alle Agenten-Schreibwege freigegeben?"""
    return _registry().get("agent_write_phase") == DEVELOPMENT_PHASE


def _entries() -> list[dict]:
    registry = _registry()
    entries = registry.get("write_capabilities") if registry else None
    return entries if isinstance(entries, list) and all(isinstance(x, dict) for x in entries) else []


def _capability(name: str, endpoint: str, screen_id: str, action_key: str) -> dict | None:
    entries = _entries()
    matches = [entry for entry in entries if entry.get("domain_command") == name and entry.get("endpoint") == endpoint
               and entry.get("screen_id") == screen_id and entry.get("action") == action_key]
    # Explicit screen aliases may share a domain command and endpoint. The
    # screen/action binding itself must still be unique, including conflicts.
    if (len(matches) != 1
            or sum(entry.get("screen_id") == screen_id and entry.get("action") == action_key for entry in entries) != 1):
        return None
    return matches[0]


def capability_enabled(name: str, endpoint: str, screen_id: str, action_key: str) -> bool:
    if development_release():
        return isinstance(endpoint, str) and endpoint.startswith("/api/v1/")
    capability = _capability(name, endpoint, screen_id, action_key)
    roles = capability.get("agent_roles") if capability else None
    return bool(isinstance(name, str) and name.endswith(".v1") and capability and capability.get("agent_write_enabled") is True
                and type(capability.get("command_version")) is int and capability["command_version"] == 1
                and isinstance(roles, list) and roles and all(isinstance(role, str) and role for role in roles))


def authorize_agent(principal, name: str, endpoint: str, screen_id: str, action_key: str) -> None:
    scopes = getattr(principal, "scopes", None)
    if development_release():
        if not isinstance(scopes, (set, frozenset)) or "masks:write" not in scopes:
            raise HTTPException(403, "Agenten-Schreibzugriff braucht masks:write")
        return
    capability = _capability(name, endpoint, screen_id, action_key)
    scopes = getattr(principal, "scopes", None)
    roles = getattr(principal, "roles", None)
    if (not capability_enabled(name, endpoint, screen_id, action_key) or not capability
            or not isinstance(scopes, (set, frozenset)) or "masks:write" not in scopes
            or not isinstance(roles, (set, frozenset)) or not roles.intersection(capability["agent_roles"])):
        raise HTTPException(403, "Agenten-Capability oder Rolle nicht freigeschaltet")
