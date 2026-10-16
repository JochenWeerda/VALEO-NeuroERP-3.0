"""SD-Studio Draft-Validierung (UIX-090) — harte Sicherheitsregeln.

No-Code-Admins bauen ScreenDefinitions im Studio; die Ausgabe ist eine NORMALE
SD, die durch dieselben Gates muss. Diese Validierung ist die Server-seitige
Zweitverteidigung: verbotene Eingaben werden ABGELEHNT (nicht bereinigt), damit
ein Draft die Sicherheits-/Vertragsgarantien nie aufweichen kann.

Reine Funktionen, keine DB. Verletzungen als Liste (leer = ok).
Regeln:
  - Namensraum: screen_id muss unter 'tenant/<slug>' liegen; native screen_ids
    duerfen weder ueberschrieben noch beschattet werden.
  - adapter muss native, temporary=True und an die eigene screen_id gebunden sein.
  - Actions nur aus dem kuratierten Katalog; eigener/fremder commandEndpoint
    verboten; dangerLevel darf ERHOEHT, nie gesenkt werden; forbiddenForAgents
    darf weder durch Weglassen noch durch Typumdeutung aufgehoben werden.
  - Reiter-, Tabellen-, Zeilen- und Agentenvertragsaktionen folgen denselben
    Katalogregeln; alternative Methoden, Commands und Eingabewege sind verboten.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "studio_data_sources.yaml"

_DANGER_RANK = {"safe": 0, "moderate": 1, "high": 2, "critical": 3}


class StudioConfigError(RuntimeError):
    pass


@lru_cache(maxsize=2)
def load_studio_catalog() -> dict[str, Any]:
    if not _CONFIG_PATH.exists():
        raise StudioConfigError(f"Studio-Katalog fehlt: {_CONFIG_PATH}")
    data = yaml.safe_load(_CONFIG_PATH.read_text(encoding="utf-8")) or {}
    actions = {a["key"]: a for a in data.get("command_actions", []) if a.get("key")}
    data_sources = list(data.get("data_sources") or [])
    endpoints = {ds["endpoint"] for ds in data_sources if ds.get("endpoint")}
    return {
        "actions": actions,
        "data_sources": data_sources,
        "command_actions": list(data.get("command_actions") or []),
        "data_source_endpoints": endpoints,
        "version": data.get("version"),
    }


def _nodes(value: Any):
    """Every metadata object, including tables inside tabs/sections."""
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from _nodes(child)


def _iter_actions(definition: dict[str, Any]):
    for node in _nodes(definition):
        for key in ("actions", "rowActions", "availableActions"):
            if key in node:
                actions = node[key]
                yield from actions if isinstance(actions, list) else [None]


def validate_studio_draft(
    definition: dict[str, Any],
    *,
    native_screen_ids: set[str],
    catalog: dict[str, Any] | None = None,
) -> list[str]:
    """Prueft einen Studio-Draft gegen die harten Sicherheitsregeln.

    Rueckgabe: Liste der Verletzungen (leer = gueltig). Der Aufrufer LEHNT bei
    nicht-leerer Liste ab (400) — es wird NICHT bereinigt.
    """
    cat = catalog or load_studio_catalog()
    catalog_actions: dict[str, Any] = cat["actions"]
    violations: list[str] = []

    # ── Struktur (Minimalkontrakt) ───────────────────────────────────────────
    for req in ("schemaVersion", "id", "domain", "mode", "title"):
        if not definition.get(req):
            violations.append(f"pflichtfeld_fehlt:{req}")
    if type(definition.get("schemaVersion")) is not int or definition.get("schemaVersion") != 1:
        violations.append("schemaVersion_muss_1_sein")

    screen_id = definition.get("id", "")
    if not isinstance(screen_id, str):
        violations.append("screen_id_muss_text_sein")
        screen_id = ""

    binding = definition.get("documentVariant")
    if binding is not None:
        try:
            from app.core.document_screen_versions import document_definition
            if not isinstance(binding, dict):
                raise ValueError("binding_not_an_object")
            document_definition(binding["variantId"], binding["variantVersion"], expected=binding)
            if definition.get("variant", {}).get("belegart") != binding["variantId"]:
                raise ValueError("variant_mismatch")
        except (ValueError, KeyError, TypeError, AttributeError):
            violations.append("belegvariantenbindung_ungueltig")

    # ── Namensraum ───────────────────────────────────────────────────────────
    if screen_id and not screen_id.startswith("tenant/"):
        violations.append(f"namensraum:screen_id_muss_tenant_prefix_haben:{screen_id}")
    if screen_id in native_screen_ids:
        violations.append(f"kollision:native_screen_id_ueberschrieben:{screen_id}")

    # ── temporary darf nicht False sein ──────────────────────────────────────
    adapter = definition.get("adapter") or {}
    if not isinstance(adapter, dict):
        violations.append("adapter_muss_objekt_sein")
        adapter = {}
    if adapter.get("temporary") is not True:
        violations.append("adapter_temporary_false_verboten" if adapter.get("temporary") is False else "adapter_temporary_true_erforderlich")
    if adapter.get("type") != "native" or adapter.get("sourceId") != screen_id:
        violations.append("adapter_muss_native_und_an_screen_id_gebunden_sein")

    allowed_endpoints: set[str] = cat.get("data_source_endpoints") or set()
    write_endpoints = {action.get("commandEndpoint") for action in catalog_actions.values()}
    write_endpoints.update((action.get("inputFlow") or {}).get("submitEndpoint")
                           for action in catalog_actions.values())
    for node in _nodes(definition):
        for field in ("endpoint", "summaryEndpoint", "countEndpoint"):
            endpoint = node.get(field)
            if endpoint is not None and (not isinstance(endpoint, str) or endpoint not in allowed_endpoints):
                violations.append(f"datenquelle_nicht_im_katalog:{endpoint}")
        for field in ("reprojectEndpoint", "icsTokenEndpoint", "submitEndpoint"):
            endpoint = node.get(field)
            if endpoint is not None and (not isinstance(endpoint, str) or endpoint not in write_endpoints):
                violations.append("schreibender_transport_nicht_im_katalog")
        if node.get("creation") not in (None, {}):
            violations.append("erstellung_nicht_im_studio_katalog")
        for field in ("rowRouteTemplate", "targetRoute", "activateRouteTemplate"):
            route = node.get(field)
            if route is not None and (not isinstance(route, str) or not route.startswith("/")
                    or route.startswith("//") or "\\" in route
                    or any(ord(char) < 32 or ord(char) == 127 for char in route)):
                violations.append("navigation_muss_lokaler_maskenpfad_sein")
        sources = node.get("dataSources", [])
        if not isinstance(sources, list):
            violations.append("datenquellen_muss_liste_sein")
            continue
        if "optionsSource" in node:
            sources = [*sources, node["optionsSource"]]
        for source in sources:
            if not isinstance(source, dict):
                violations.append("datenquelle_muss_objekt_sein")
                continue

    # ── Actions ──────────────────────────────────────────────────────────────
    for action in _iter_actions(definition):
        if not isinstance(action, dict):
            violations.append("action_muss_objekt_sein")
            continue
        key = action.get("key", "")
        if not isinstance(key, str):
            violations.append("action_key_muss_text_sein")
            continue
        base = catalog_actions.get(key)
        if base is None:
            violations.append(f"action_nicht_im_katalog:{key}")
            continue
        # eigener/fremder commandEndpoint
        ep = action.get("commandEndpoint")
        if ep is not None and ep != base.get("commandEndpoint"):
            violations.append(f"action_fremder_commandEndpoint:{key}")
        # dangerLevel darf nicht gesenkt werden
        draft_danger = action.get("dangerLevel", "safe")
        if not isinstance(draft_danger, str) or draft_danger not in _DANGER_RANK:
            violations.append(f"action_ungueltiger_dangerLevel:{key}:{draft_danger}")
        elif _DANGER_RANK[draft_danger] < _DANGER_RANK[base["dangerLevel"]]:
            violations.append(f"action_dangerLevel_gesenkt:{key}")
        # Transport identifiers cannot select an alternative command or human form.
        for field in ("command", "commandBinding", "inputFlow", "navigationRoute"):
            if field in action and action[field] != base.get(field):
                violations.append(f"action_fremder_{field}:{key}")
        if action.get("method", "POST") != base.get("method", "POST"):
            violations.append(f"action_fremde_methode:{key}")
        if "permission" in action and action["permission"] != base.get("permission", "studio.draft.execute"):
            violations.append(f"action_fremdes_recht:{key}")
        if base.get("permission") and action.get("permission") != base["permission"]:
            violations.append(f"action_recht_fehlt:{key}")
        for flag in ("forbiddenForAgents", "humanApprovalRequired", "requiresHumanApproval", "auditReasonRequired", "requiresConfirmation", "disabled"):
            if base.get(flag) is True and action.get(flag) is not True:
                violations.append(f"action_{flag}_aufgehoben:{key}")
            elif flag in action and type(action[flag]) is not bool:
                violations.append(f"action_{flag}_muss_boolean_sein:{key}")
        effective_danger = draft_danger if isinstance(draft_danger, str) and draft_danger in _DANGER_RANK else base.get("dangerLevel")
        if (
            effective_danger in _DANGER_RANK
            and _DANGER_RANK[effective_danger] >= _DANGER_RANK["high"]
            and not action.get("requiresConfirmation")
        ):
            violations.append(f"action_confirmation_fehlt:{key}")

    # Explicit agent contracts may describe the UI, but cannot weaken its policy.
    declared: dict[str, list[dict[str, Any]]] = {}
    for node in _nodes(definition):
        for collection in ("actions", "rowActions"):
            for action in node.get(collection, []) if isinstance(node.get(collection, []), list) else []:
                if isinstance(action, dict) and isinstance(action.get("key"), str):
                    declared.setdefault(action["key"], []).append(action)
    contract = definition.get("agentContract") or {}
    if not isinstance(contract, dict):
        violations.append("agentContract_muss_objekt_sein")
        contract = {}
    agent_actions = contract.get("availableActions", [])
    for action in agent_actions if isinstance(agent_actions, list) else []:
        if not isinstance(action, dict) or not isinstance(action.get("key"), str):
            continue  # structural violation already collected above
        key = action["key"]
        if key not in declared:
            violations.append(f"agent_action_ohne_maskenaktion:{key}")
        for screen_action in declared.get(key, []):
            ui_rank = _DANGER_RANK.get(str(screen_action.get("dangerLevel", "safe")), 0)
            agent_rank = _DANGER_RANK.get(str(action.get("dangerLevel", "safe")), -1)
            if agent_rank < ui_rank:
                violations.append(f"agent_action_dangerLevel_gesenkt:{key}")
            if screen_action.get("permission") and action.get("permission") != screen_action["permission"]:
                violations.append(f"agent_action_recht_widerspricht_maske:{key}")
            for ui_flag, agent_flag in (("requiresConfirmation", "requiresConfirmation"),
                                       ("humanApprovalRequired", "requiresHumanApproval"),
                                       ("forbiddenForAgents", "forbiddenForAgents")):
                if screen_action.get(ui_flag) is True and action.get(agent_flag) is not True:
                    violations.append(f"agent_action_{agent_flag}_aufgehoben:{key}")

    from app.services.studio_semantic import semantic_violations
    violations.extend(semantic_violations(definition))
    return violations
