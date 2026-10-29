"""Deterministischer Resolver: Kurzkommando → typisierte Fachaktion.

Kein LLM. Alias- und Action-ID-Match, danach Scope- und Vier-Augen-Pruefung.
Keine Datenbankzugriffe.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml

_CATALOG_PATH = Path(__file__).resolve().parents[2] / "config" / "adaptive_workspace_fachaktionen.yaml"
_FILLERS = frozenset(
    {
        "zeige",
        "zeig",
        "welche",
        "welcher",
        "welches",
        "liste",
        "list",
        "oeffne",
        "offen",
        "der",
        "die",
        "das",
        "alle",
        "mir",
        "bitte",
        "sind",
        "ist",
        "den",
        "dem",
        "ein",
        "eine",
        "einen",
        "fuer",
        "zum",
        "zur",
        "und",
        "von",
        "im",
        "in",
    }
)
_UMLAUT = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})
_NON_ALNUM = re.compile(r"[^a-z0-9.]+")


class WorkspaceFachaktionenError(ValueError):
    """Katalog ist ungueltig (Kollision, Pflichtfeld fehlt)."""


@dataclass(frozen=True)
class Resolution:
    action_id: str | None
    authorized: bool
    reason: str
    command_normalized: str
    action: dict[str, Any] | None
    matched_alias: str | None = None

    def as_dict(self) -> dict[str, Any]:
        action = self.action or {}
        return {
            "action_id": self.action_id,
            "authorized": self.authorized,
            "reason": self.reason,
            "command_normalized": self.command_normalized,
            "matched_alias": self.matched_alias,
            "access": action.get("access"),
            "risk_level": action.get("risk_level"),
            "four_eyes": bool(action.get("four_eyes")),
            "forbidden_for_agents": bool(action.get("forbidden_for_agents")),
            "enabled_for_agents": bool(action.get("enabled_for_agents")),
            "permission": action.get("permission") or {},
            "idempotency": action.get("idempotency"),
            "audit": action.get("audit"),
            "event_out": action.get("event_out") or [],
            "mcp_tool_id": action.get("mcp_tool_id"),
            "mask_action_id": action.get("mask_action_id"),
            "command_endpoint": action.get("command_endpoint"),
            "screen_id": action.get("screen_id"),
            "route_path": action.get("route_path"),
            "follow_up_writes": action.get("follow_up_writes") or [],
            "executable": bool(action.get("executable", True)),
            "execute_via": "mcp" if action.get("mcp_tool_id") else "rest_or_gap",
        }


def normalize_command(text: str) -> str:
    raw = (text or "").strip().lower().translate(_UMLAUT)
    raw = _NON_ALNUM.sub(" ", raw)
    tokens = [tok for tok in raw.split() if tok and tok not in _FILLERS]
    return " ".join(tokens)


def _require(action: dict[str, Any], field: str) -> None:
    if field not in action or action[field] in (None, ""):
        raise WorkspaceFachaktionenError(
            f"Action {action.get('action_id', '?')} fehlt Pflichtfeld '{field}'"
        )


def _validate_catalog(data: Mapping[str, Any]) -> list[dict[str, Any]]:
    actions = data.get("actions")
    if not isinstance(actions, list) or not actions:
        raise WorkspaceFachaktionenError("Katalog ohne actions")
    seen_ids: set[str] = set()
    alias_owner: dict[str, str] = {}
    for raw in actions:
        if not isinstance(raw, dict):
            raise WorkspaceFachaktionenError("Action-Eintrag ist kein Objekt")
        for field in (
            "action_id",
            "domain",
            "access",
            "risk_level",
            "permission",
            "idempotency",
            "audit",
        ):
            _require(raw, field)
        action_id = str(raw["action_id"])
        if action_id in seen_ids:
            raise WorkspaceFachaktionenError(f"Doppelte Action-ID: {action_id}")
        seen_ids.add(action_id)
        perm = raw.get("permission") or {}
        if not perm.get("scope"):
            raise WorkspaceFachaktionenError(f"{action_id}: permission.scope fehlt")
        access = raw.get("access")
        if access == "write" and raw.get("idempotency") not in {"required", "not_required"}:
            raise WorkspaceFachaktionenError(f"{action_id}: write braucht idempotency")
        if access == "write" and not raw.get("audit"):
            raise WorkspaceFachaktionenError(f"{action_id}: write braucht audit")
        if raw.get("four_eyes") and access != "write":
            raise WorkspaceFachaktionenError(f"{action_id}: four_eyes nur bei write")
        for alias in raw.get("aliases") or []:
            key = normalize_command(str(alias))
            if not key:
                raise WorkspaceFachaktionenError(f"{action_id}: leerer Alias")
            owner = alias_owner.get(key)
            if owner and owner != action_id:
                raise WorkspaceFachaktionenError(
                    f"Alias-Kollision '{key}': {owner} vs {action_id}"
                )
            alias_owner[key] = action_id
    return [dict(a) for a in actions]


@lru_cache(maxsize=4)
def load_catalog(path: str | None = None) -> dict[str, Any]:
    catalog_path = Path(path) if path else _CATALOG_PATH
    data = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
    actions = _validate_catalog(data)
    alias_index: dict[str, str] = {}
    by_id: dict[str, dict[str, Any]] = {}
    for action in actions:
        by_id[action["action_id"]] = action
        alias_index[normalize_command(action["action_id"])] = action["action_id"]
        for alias in action.get("aliases") or []:
            alias_index[normalize_command(str(alias))] = action["action_id"]
    return {
        "meta": {
            "registry_id": data.get("registry_id"),
            "schema_version": data.get("schema_version"),
            "lead_contract": data.get("lead_contract") or {},
            "canonical_events": data.get("canonical_events") or {},
            "event_gaps": data.get("event_gaps") or [],
        },
        "actions": actions,
        "by_id": by_id,
        "alias_index": alias_index,
        "path": str(catalog_path),
    }


def list_catalog(*, access: str | None = None) -> dict[str, Any]:
    catalog = load_catalog()
    actions = catalog["actions"]
    if access:
        actions = [a for a in actions if a.get("access") == access]
    return {
        "registry_id": catalog["meta"]["registry_id"],
        "schema_version": catalog["meta"]["schema_version"],
        "path": catalog["path"],
        "lead_contract": catalog["meta"]["lead_contract"],
        "canonical_events": catalog["meta"]["canonical_events"],
        "event_gaps": catalog["meta"]["event_gaps"],
        "count": len(actions),
        "actions": [
            {
                "action_id": a["action_id"],
                "example_query": a.get("example_query"),
                "domain": a.get("domain"),
                "access": a.get("access"),
                "risk_level": a.get("risk_level"),
                "scope": (a.get("permission") or {}).get("scope"),
                "four_eyes": bool(a.get("four_eyes")),
                "forbidden_for_agents": bool(a.get("forbidden_for_agents")),
                "enabled_for_agents": bool(a.get("enabled_for_agents")),
                "idempotency": a.get("idempotency"),
                "audit": a.get("audit"),
                "event_out": a.get("event_out") or [],
                "mcp_tool_id": a.get("mcp_tool_id"),
                "mask_action_id": a.get("mask_action_id"),
                "command_endpoint": a.get("command_endpoint"),
                "screen_id": a.get("screen_id"),
                "route_path": a.get("route_path"),
                "aliases": a.get("aliases") or [],
                "follow_up_writes": a.get("follow_up_writes") or [],
                "executable": bool(a.get("executable", True)),
            }
            for a in actions
        ],
    }


def _has_scope(scopes: Iterable[str], required: str) -> bool:
    held = set(scopes)
    if "admin:all" in held:
        return True
    return required in held


def _inflection_variants(command: str) -> list[str]:
    """Deterministische Adjektiv-Flexion: ueberfaelligen → ueberfaellige."""
    variants = [command]
    tokens = command.split()
    alt = [
        tok[:-2] + "e" if tok.endswith("en") and len(tok) > 8 else tok
        for tok in tokens
    ]
    alt_s = " ".join(alt)
    if alt_s != command:
        variants.append(alt_s)
    return variants


def _phrase_hits(command: str, alias: str) -> bool:
    if not alias or not command:
        return False
    if command == alias:
        return True
    return re.search(r"\b" + re.escape(alias) + r"\b", command) is not None


def _match_action(command: str, catalog: Mapping[str, Any]) -> tuple[dict[str, Any] | None, str | None, str]:
    by_id = catalog["by_id"]
    alias_index: dict[str, str] = catalog["alias_index"]
    for variant in _inflection_variants(command):
        if variant in by_id:
            return by_id[variant], variant, "action_id"
        if variant in alias_index:
            action_id = alias_index[variant]
            return by_id[action_id], variant, "alias_exact"

    best_by_action: dict[str, tuple[int, str]] = {}
    for alias, action_id in alias_index.items():
        if not _phrase_hits(command, alias):
            continue
        prev = best_by_action.get(action_id)
        if prev is None or len(alias) > prev[0]:
            best_by_action[action_id] = (len(alias), alias)
    if not best_by_action:
        return None, None, "unknown"
    ranked = sorted(
        ((length, alias, action_id) for action_id, (length, alias) in best_by_action.items()),
        key=lambda item: (-item[0], item[1], item[2]),
    )
    longest = ranked[0][0]
    tied = [item for item in ranked if item[0] == longest]
    if len(tied) > 1:
        return None, None, "ambiguous"
    _, alias, action_id = ranked[0]
    return by_id[action_id], alias, "alias_phrase"


def authorize_action(
    action: Mapping[str, Any],
    *,
    scopes: Iterable[str],
    identity_type: str | None,
) -> tuple[bool, str]:
    required = str((action.get("permission") or {}).get("scope") or "")
    if not _has_scope(scopes, required):
        return False, "missing_scope"
    identity = (identity_type or "agent").strip().lower()
    is_human = identity == "human"
    if action.get("forbidden_for_agents") and not is_human:
        return False, "forbidden_for_agents"
    if action.get("access") == "write" and not action.get("enabled_for_agents") and not is_human:
        return False, "write_not_enabled_for_agents"
    if (
        action.get("four_eyes")
        and action.get("access") == "write"
        and action.get("risk_level") == "R4"
        and not is_human
    ):
        return False, "four_eyes_requires_human"
    return True, "authorized"


def resolve_command(
    command: str,
    *,
    scopes: Iterable[str] | None = None,
    identity_type: str | None = "agent",
    catalog_path: str | None = None,
) -> Resolution:
    normalized = normalize_command(command)
    catalog = load_catalog(catalog_path)
    if not normalized:
        return Resolution(
            action_id=None,
            authorized=False,
            reason="empty_command",
            command_normalized=normalized,
            action=None,
        )
    action, matched, kind = _match_action(normalized, catalog)
    if action is None:
        return Resolution(
            action_id=None,
            authorized=False,
            reason=kind,
            command_normalized=normalized,
            action=None,
            matched_alias=matched,
        )
    ok, reason = authorize_action(action, scopes=scopes or (), identity_type=identity_type)
    return Resolution(
        action_id=action["action_id"],
        authorized=ok,
        reason=reason,
        command_normalized=normalized,
        action=action,
        matched_alias=matched if kind != "action_id" else None,
    )


def execute_mcp(request: Any, actor: str, tenant: str, user: Mapping[str, Any]) -> dict[str, Any]:
    """Lesende MCP-Adapter fuer Katalog und Aufloesung. Kein DB-Write."""
    tool = getattr(request, "tool_name", "")
    params = dict(getattr(request, "parameters", None) or {})
    raw = user.get("raw") if isinstance(user.get("raw"), dict) else {}
    identity_type = raw.get("identity_type") or "agent"
    scopes = user.get("scopes") or []
    if tool == "workspace.fachaktion.katalog":
        access = params.get("access")
        if access is not None and access not in {"read", "write"}:
            from fastapi import HTTPException

            raise HTTPException(422, "access muss read oder write sein")
        payload = list_catalog(access=access)
        return {
            "success": True,
            "mode": getattr(request, "mode", "dryRun"),
            "actor": actor,
            "tenant_id": tenant,
            **payload,
        }
    if tool == "workspace.fachaktion.resolve":
        command = params.get("command")
        if not isinstance(command, str) or not command.strip():
            from fastapi import HTTPException

            raise HTTPException(422, "command fehlt")
        resolution = resolve_command(command, scopes=scopes, identity_type=str(identity_type))
        return {
            "success": True,
            "mode": getattr(request, "mode", "dryRun"),
            "actor": actor,
            "tenant_id": tenant,
            **resolution.as_dict(),
        }
    from fastapi import HTTPException

    raise HTTPException(501, "Unknown workspace tool")
