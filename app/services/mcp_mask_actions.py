"""Generische MCP-Werkzeuge fuer Maskenaktionen — eine Fachaktion, derselbe Kommandoweg wie die Maske.

``mask.actions.list`` liest die Aktionen einer Maske aus derselben mandantengenauen ScreenDefinition, die die
Maske und die CLI lesen. ``mask.action.execute`` ruft den deklarierten Kommando-Endpunkt mit dem Bearer-Token des
Aufrufers und demselben Umschlag wie ``useActionRuntime`` (``_mode``, ``_auditReason``, ``_idempotencyKey``).
Rechte, Mandant, Audit und Wiederholungsschutz prueft der Ziel-Endpunkt; dieses Modul gewaehrt nichts.

Was die Maske Agenten nicht erlaubt, erlaubt auch dieses Werkzeug nicht: ``forbiddenForAgents``,
``humanApprovalRequired``, versionierte Command-Adapter (Belege, Ernte-Steuerung), Eingabefluesse nur in der
Maske und Aktionen ohne Kommando-Endpunkt. Die Regel ist dieselbe wie ``valeo_cli.support`` (Paritaetstest).
"""
from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx
import yaml
from fastapi import HTTPException

TOOLS = {"mask.actions.list", "mask.action.execute"}
_PLACEHOLDER = re.compile(r"\{[^}]+\}")
_GENERIC_PARAMETERS = {"{entity_id}", "{screen_id}"}
_DOCFLOW = re.compile(r"^/api/v1/docflow(?:/|$)")
_IDENTITY_BUDGET = re.compile(r"^/api/v1/identity/budgets/actions/(root|allocate)$")
_SCREEN_ID = re.compile(r"^[a-z0-9][a-z0-9_/-]{0,120}$")
_ENVELOPE = {"_mode", "_auditReason", "_idempotencyKey"}
#: Wie _FORBIDDEN_PARAMETER_IDENTITY_KEYS der MCP-Ausfuehrung: Identitaet kommt nur aus dem Token.
_IDENTITY_KEYS = {"tenant_id", "mandanten_id", "bediener", "approval_granted", "actor", "user_id", "performed_by"}


def agent_block(action: dict[str, Any]) -> str | None:
    """Warum ein Agent diese Aktion nicht ausfuehren darf — oder ``None``."""
    if action.get("inputFlow"):
        return "eingabe_in_maske"
    endpoint = action.get("commandEndpoint")
    if not endpoint:
        return "kein_endpunkt"
    if action.get("commandBinding"):
        return "adapter_nur_mensch"
    if _DOCFLOW.match(endpoint):
        return "docflow_ohne_adapter"
    if set(_PLACEHOLDER.findall(endpoint)) - _GENERIC_PARAMETERS:
        return "pfadparameter_nur_adapter"
    if action.get("forbiddenForAgents"):
        return "fuer_agenten_gesperrt"
    if action.get("humanApprovalRequired"):
        return "menschliche_genehmigung"
    return None


def iter_actions(definition: dict[str, Any]):
    seen: set[str] = set()
    stack: list[Any] = [definition]
    while stack:
        node = stack.pop(0)
        if isinstance(node, dict):
            for key in ("actions", "rowActions", "availableActions"):
                for action in node.get(key) or []:
                    if isinstance(action, dict) and action.get("key") and action["key"] not in seen:
                        seen.add(action["key"])
                        yield action
            stack.extend(v for k, v in node.items() if k not in ("actions", "rowActions", "availableActions"))
        elif isinstance(node, list):
            stack.extend(node)


def _definition(screen_id: Any, tenant: str) -> dict[str, Any]:
    from app.core.screen_definitions import get_screen_definition

    if not isinstance(screen_id, str) or not _SCREEN_ID.match(screen_id):
        raise HTTPException(422, "screen_id fehlt oder ist ungueltig")
    from app.services.studio_draft_store import StudioStorageUnavailable

    try:
        definition = get_screen_definition(screen_id, tenant_id=tenant)
    except StudioStorageUnavailable as exc:
        raise HTTPException(503, "Studio-Masken derzeit nicht verfuegbar") from exc
    if definition is None:
        raise HTTPException(404, "Keine Maske mit dieser Kennung im Mandanten")
    return definition


def list_actions(parameters: dict[str, Any], tenant: str) -> dict[str, Any]:
    definition = _definition(parameters.get("screen_id"), tenant)
    rows = []
    for action in iter_actions(definition):
        block = agent_block(action)
        rows.append({"key": action["key"], "label": action.get("label"), "agent_ausfuehrbar": block is None,
                     "grund": block, "danger_level": action.get("dangerLevel", "safe"),
                     "requires_confirmation": bool(action.get("requiresConfirmation")),
                     "audit_reason_required": bool(action.get("auditReasonRequired")),
                     "needs_entity_id": "{entity_id}" in (action.get("commandEndpoint") or ""),
                     "input_fields": [{k: f.get(k) for k in ("key", "label", "type", "required", "options") if k in f}
                                      for f in action.get("inputFields") or [] if isinstance(f, dict)]})
    return {"success": True, "screen_id": definition.get("id"), "title": definition.get("title"), "actions": rows}


HUMAN_ONLY = {"fuer_agenten_gesperrt", "menschliche_genehmigung"}


@lru_cache(maxsize=1)
def _tool_mask_actions() -> dict[str, tuple[tuple[str, str], ...]]:
    """MCP-Werkzeug -> zugeordnete Maskenaktionen (screen_id, action_key) laut config/mcp_mask_action_map.yaml."""
    path = Path(__file__).resolve().parents[2] / "config/mcp_mask_action_map.yaml"
    mappings = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("mappings", [])
    out: dict[str, list[tuple[str, str]]] = {}
    for m in mappings:
        tool, mask_action = m.get("mcp_tool_id"), m.get("mask_action_id") or ""
        if tool and mask_action.startswith("mask:") and mask_action.count(":") >= 2:
            _, screen, key = mask_action.split(":", 2)
            out.setdefault(tool, []).append((screen, key))
    return {tool: tuple(v) for tool, v in out.items()}


def human_only_tool_call(tool_name: str, parameters: dict[str, Any]) -> str | None:
    """Die Maskenaktion, die ein Spezialwerkzeug ausloest, wenn die Maske sie Menschen vorbehaelt — sonst ``None``.

    Die Maske ist die Quelle der Agentengrenze: ``forbiddenForAgents`` und ``humanApprovalRequired`` gelten fuer
    jeden Zugang. Werkzeuge mit mehreren Zielaktionen waehlen sie ueber ``action_key``; ist keine Auswahl erkennbar,
    gilt im Zweifel die strengste zugeordnete Aktion.
    """
    from app.core.screen_definitions import get_screen_definition

    candidates = _tool_mask_actions().get(tool_name, ())
    selected = parameters.get("action_key") if isinstance(parameters, dict) else None
    if isinstance(selected, str) and any(key == selected for _, key in candidates):
        candidates = tuple((screen, key) for screen, key in candidates if key == selected)
    for screen, key in candidates:
        definition = get_screen_definition(screen) or {}
        action = next((a for a in iter_actions(definition) if a["key"] == key), None)
        if action is not None and agent_block(action) in HUMAN_ONLY:
            return f"mask:{screen}:{key}"
    return None


def _identity_budget_input(endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
    match = _IDENTITY_BUDGET.match(endpoint)
    if not match:
        return payload
    fields = ["tokens", "max_children"] + ([] if match.group(1) == "root" else ["parent", "owner", "kind", "request_id"])
    return {key: payload[key] for key in fields if key in payload}


def _base_url() -> str:
    # Derselbe Server, dieselbe Route: die Ausfuehrung durchlaeuft Auth-, Mandanten- und Rechtepruefung erneut.
    return os.environ.get("MASK_ACTION_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def execute(request: Any, tenant: str, authorization: str | None, *, transport: httpx.BaseTransport | None = None) -> dict:
    parameters = dict(request.parameters)
    screen_id, action_key = parameters.pop("screen_id", None), parameters.pop("action", None)
    entity_id, payload = parameters.pop("entity_id", None), parameters.pop("input", {}) or {}
    audit_reason = parameters.pop("audit_reason", None)
    if parameters:
        raise HTTPException(422, "Unbekannte Parameter: " + ", ".join(sorted(parameters)))
    if not isinstance(payload, dict) or _ENVELOPE & set(payload):
        raise HTTPException(422, "input muss ein Objekt ohne Umschlagfelder sein")
    if _IDENTITY_KEYS & set(payload):
        raise HTTPException(422, "Identitaetsfelder sind in input nicht erlaubt: " + ", ".join(sorted(_IDENTITY_KEYS & set(payload))))
    if not isinstance(authorization, str) or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Bearer-Token des Aufrufers fehlt")
    definition = _definition(screen_id, tenant)
    action = next((a for a in iter_actions(definition) if a["key"] == action_key), None)
    if action is None:
        raise HTTPException(404, "Die Maske hat diese Aktion nicht")
    block = agent_block(action)
    if block:
        raise HTTPException(403, f"Aktion fuer MCP-Agenten nicht freigegeben: {block}")
    if request.mode == "execute" and not (request.idempotency_key or "").strip():
        raise HTTPException(422, "execute requires an idempotency_key")
    if request.mode == "execute" and action.get("auditReasonRequired") and not (audit_reason or "").strip():
        raise HTTPException(422, "Diese Aktion verlangt audit_reason")
    endpoint = action["commandEndpoint"]
    if "{entity_id}" in endpoint and not (isinstance(entity_id, str) and entity_id.strip()):
        raise HTTPException(422, "Diese Aktion braucht entity_id")
    path = endpoint.replace("{entity_id}", quote(entity_id or "", safe="")).replace("{screen_id}", definition["id"])
    body: dict[str, Any] = dict(_identity_budget_input(endpoint, payload))
    if request.mode != "execute":
        body["_mode"] = request.mode
    if audit_reason:
        body["_auditReason"] = audit_reason
    if request.idempotency_key:
        body["_idempotencyKey"] = request.idempotency_key
    with httpx.Client(base_url=_base_url(), timeout=60.0, transport=transport) as client:
        # Kein Mandanten-Header: der Ziel-Endpunkt nimmt den Mandanten allein aus dem Token (wie Maske und CLI).
        response = client.request((action.get("method") or "POST").upper(), path, json=body,
                                  headers={"Authorization": authorization})
    try:
        data = response.json()
    except ValueError:
        data = {"detail": response.text[:300]}
    if response.status_code >= 400:
        detail = data.get("detail") if isinstance(data, dict) else data
        raise HTTPException(response.status_code, detail if isinstance(detail, str) else "Aktion abgelehnt")
    return {"success": not (isinstance(data, dict) and data.get("success") is False), "screen_id": definition["id"],
            "action": action["key"], "mode": request.mode, "result": data}
