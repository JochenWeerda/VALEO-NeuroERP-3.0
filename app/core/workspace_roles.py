"""Rollen-Workspace-Aufloesung (UIX-061).

Liest config/workspace_roles.yaml (Rolle → cockpit-ScreenDefinition) mit
optionalen Tenant-Overrides und loest die reale Startseiten-Route ueber die
Omnibox-Routen-Bruecke auf. Reine Konfiguration — keine DB, keine Secrets.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from app.core.screen_definitions import get_screen_list_route

_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "workspace_roles.yaml"


@lru_cache(maxsize=1)
def _load_config() -> dict[str, Any]:
    if not _CONFIG_PATH.exists():
        return {"default": {}, "tenant_overrides": {}}
    data = yaml.safe_load(_CONFIG_PATH.read_text(encoding="utf-8")) or {}
    data.setdefault("default", {})
    data.setdefault("tenant_overrides", {})
    return data


def _normalize_role(role: str | None) -> str:
    return (role or "").strip().lower()


def resolve_workspace_screen(role: str | None, tenant_id: str | None = None) -> str | None:
    """ScreenDefinition-ID der Rollen-Startseite; None wenn keine Zuordnung."""
    config = _load_config()
    key = _normalize_role(role)
    if not key:
        return None
    overrides = config.get("tenant_overrides", {}).get(tenant_id or "", {})
    if key in overrides:
        return overrides[key]
    return config.get("default", {}).get(key)


def resolve_workspace_startpage(role: str | None, tenant_id: str | None = None) -> dict[str, Any]:
    """{role, screenId, route} — route ueber die Omnibox-Routen-Bruecke aufgeloest."""
    screen_id = resolve_workspace_screen(role, tenant_id)
    route = get_screen_list_route(screen_id) if screen_id else None
    return {"role": _normalize_role(role) or None, "screenId": screen_id, "route": route}
