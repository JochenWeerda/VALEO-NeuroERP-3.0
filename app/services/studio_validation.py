"""SD-Studio Draft-Validierung (UIX-090) — harte Sicherheitsregeln.

No-Code-Admins bauen ScreenDefinitions im Studio; die Ausgabe ist eine NORMALE
SD, die durch dieselben Gates muss. Diese Validierung ist die Server-seitige
Zweitverteidigung: verbotene Eingaben werden ABGELEHNT (nicht bereinigt), damit
ein Draft die Sicherheits-/Vertragsgarantien nie aufweichen kann.

Reine Funktionen, keine DB. Verletzungen als Liste (leer = ok).
Regeln:
  - Namensraum: screen_id muss unter 'tenant/<slug>' liegen; native screen_ids
    duerfen weder ueberschrieben noch beschattet werden.
  - adapter.temporary darf nicht False sein (Studio-SDs sind temporaer).
  - Actions nur aus dem kuratierten Katalog; eigener/fremder commandEndpoint
    verboten; dangerLevel darf ERHOEHT, nie gesenkt werden; forbiddenForAgents
    darf nicht aufgehoben werden.
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
    endpoints = {ds["endpoint"] for ds in data.get("data_sources", []) if ds.get("endpoint")}
    return {"actions": actions, "data_source_endpoints": endpoints, "version": data.get("version")}


def _iter_actions(definition: dict[str, Any]):
    return definition.get("actions") or []


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
    if definition.get("schemaVersion") not in (None, 1):
        violations.append("schemaVersion_muss_1_sein")

    screen_id = definition.get("id", "")

    # ── Namensraum ───────────────────────────────────────────────────────────
    if screen_id and not screen_id.startswith("tenant/"):
        violations.append(f"namensraum:screen_id_muss_tenant_prefix_haben:{screen_id}")
    if screen_id in native_screen_ids:
        violations.append(f"kollision:native_screen_id_ueberschrieben:{screen_id}")

    # ── temporary darf nicht False sein ──────────────────────────────────────
    adapter = definition.get("adapter") or {}
    if adapter.get("temporary") is False:
        violations.append("adapter_temporary_false_verboten")

    # ── Actions ──────────────────────────────────────────────────────────────
    for action in _iter_actions(definition):
        key = action.get("key", "")
        base = catalog_actions.get(key)
        if base is None:
            violations.append(f"action_nicht_im_katalog:{key}")
            continue
        # eigener/fremder commandEndpoint
        ep = action.get("commandEndpoint")
        if ep is not None and ep != base.get("commandEndpoint"):
            violations.append(f"action_fremder_commandEndpoint:{key}")
        # dangerLevel darf nicht gesenkt werden
        draft_danger = action.get("dangerLevel", base.get("dangerLevel"))
        if draft_danger not in _DANGER_RANK:
            violations.append(f"action_ungueltiger_dangerLevel:{key}:{draft_danger}")
        elif _DANGER_RANK[draft_danger] < _DANGER_RANK[base["dangerLevel"]]:
            violations.append(f"action_dangerLevel_gesenkt:{key}")
        # forbiddenForAgents darf nicht aufgehoben werden
        if base.get("forbiddenForAgents") is True and action.get("forbiddenForAgents") is False:
            violations.append(f"action_forbiddenForAgents_aufgehoben:{key}")

    return violations
