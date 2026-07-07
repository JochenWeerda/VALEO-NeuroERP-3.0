"""
Mask Registry API — Wave 3 AP1

Liefert das klassifizierte Masken-Register (A/B/C) fuer das UI-Framework.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ....core.tenant import get_tenant_id
from ....core.mask_classification import (
    MaskRegistry,
    MaskClass,
    MaskDomain,
    build_mask_registry,
)

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.mask_registry_schemas import (
    MaskRegistryOut,
    OmniboxCatalogEntryOut,
    WorkspaceStartpageOut,
)
from ....core.workspace_roles import resolve_workspace_startpage


router = APIRouter(prefix="/ui/mask-registry", tags=["ui", "masks"])

_REGISTRY: MaskRegistry = build_mask_registry()


# ── Omnibox-Katalog (UIX-060) ────────────────────────────────────────────────

_FILTER_TYPE_BY_RENDER_KIND = {
    "status": "enum",
    "date": "date",
    "datetime": "date",
    "currency": "number",
    "number": "number",
    "percentage": "number",
}


def _collect_filterable_fields(sd: dict) -> list[dict]:
    """Sammelt filterbare Tabellenspalten (top-level und je Tab) einer SD."""
    fields: dict[str, dict] = {}
    tables = list(sd.get("tables") or [])
    for tab in sd.get("tabs") or []:
        tables.extend(tab.get("tables") or [])
    for table in tables:
        for col in table.get("columns") or []:
            if not col.get("filterable"):
                continue
            key = col.get("key", "")
            if not key or key in fields:
                continue
            render_kind = col.get("renderKind", "")
            col_type = _FILTER_TYPE_BY_RENDER_KIND.get(render_kind)
            if col_type is None:
                col_type = "number" if col.get("numeric") else "text"
            fields[key] = {"key": key, "label": col.get("label", key), "type": col_type}
    return list(fields.values())


def _normalize_verb(text: str) -> str:
    return text.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")


def _collect_command_actions(sd: dict) -> list[dict]:
    """Draftbare Aktionen (mit commandEndpoint) fuer den NL-Command-Pfad (UIX-070).

    Nur die Sicherheits-relevanten Felder + Suchbegriffe + Formularfelder —
    die Sicherheitsmatrix entscheidet frontend-seitig (classifyOmniboxAction)."""
    actions: list[dict] = []
    for action in sd.get("actions") or []:
        if not action.get("commandEndpoint"):
            continue  # nur echte Mutations-Commands sind draftbar
        key = action.get("key", "")
        label = action.get("label", key)
        verbs = sorted({_normalize_verb(t) for t in (key.replace("_", " ") + " " + label).split() if len(t) > 2})
        actions.append({
            "key": key,
            "label": label,
            "dangerLevel": action.get("dangerLevel", "safe"),
            "requiresConfirmation": bool(action.get("requiresConfirmation")),
            "forbiddenForAgents": bool(action.get("forbiddenForAgents")),
            "verbs": verbs,
            "fields": [
                {"key": f.get("key"), "type": f.get("type", "text"), "required": bool(f.get("required"))}
                for f in (action.get("fields") or [])
                if f.get("key")
            ],
        })
    return actions


def _build_omnibox_catalog() -> list[dict]:
    from app.core.screen_definitions import (
        _SCREEN_DEFINITIONS,
        get_screen_definition,
        get_screen_list_route,
    )

    entries: list[dict] = []
    for screen_id in sorted(_SCREEN_DEFINITIONS.keys()):
        sd = get_screen_definition(screen_id)
        if not sd:
            continue
        contract = sd.get("agentContract") or {}
        layout = sd.get("layout") or {}
        entries.append({
            "screen_id": screen_id,
            "title": sd.get("title", screen_id),
            "domain": sd.get("domain", ""),
            "floorplan": layout.get("floorplan", ""),
            "route": get_screen_list_route(screen_id) or "",
            "synonyms": list(contract.get("synonyms") or []),
            "example_prompts": list(contract.get("examplePrompts") or []),
            "filterable_fields": _collect_filterable_fields(sd),
            "actions": _collect_command_actions(sd),
        })
    return entries


@router.get(
    "/omnibox-catalog",
    response_model=list[OmniboxCatalogEntryOut],
    summary="Omnibox catalog abrufen",
)
async def get_omnibox_catalog(tenant_id: str = Depends(get_tenant_id)):
    """Kompakter Masken-Katalog fuer den Omnibox-Intent-Compiler (UIX-060):
    Titel, Synonyme, Beispiel-Prompts und filterbare Felder je ScreenDefinition."""
    _ = tenant_id
    return _build_omnibox_catalog()


@router.get(
    "/workspace-startpage",
    response_model=WorkspaceStartpageOut,
    summary="Rollen-Startseite (Workspace) aufloesen",
)
async def get_workspace_startpage(
    role: str | None = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """Loest die rollenbasierte cockpit-Startseite auf (UIX-061). Ohne Zuordnung
    bleiben screenId/route null → Frontend faellt auf die bisherige Startseite zurueck."""
    return resolve_workspace_startpage(role, tenant_id)


@router.get("", response_model=MaskRegistryOut, summary="Mask registry abrufen")
async def get_mask_registry(tenant_id: str = Depends(get_tenant_id)):
    """Liefert das vollstaendige Masken-Register mit A/B/C-Klassifizierung."""
    _ = tenant_id
    return _REGISTRY.model_dump(mode="json")


@router.get("/class/{mask_class}", response_model=list[MaskRegistryOut], summary="Masks by class abrufen")
async def get_masks_by_class(
    mask_class: MaskClass,
    tenant_id: str = Depends(get_tenant_id),
):
    """Liefert alle Masken einer Klasse (A=Kernprozess, B=Unterstuetzend, C=Reporting)."""
    _ = tenant_id
    return [m.model_dump(mode="json") for m in _REGISTRY.get_by_class(mask_class)]


@router.get("/domain/{domain}", response_model=list[MaskRegistryOut], summary="Masks by domain abrufen")
async def get_masks_by_domain(
    domain: MaskDomain,
    tenant_id: str = Depends(get_tenant_id),
):
    """Liefert alle Masken einer fachlichen Domain."""
    _ = tenant_id
    return [m.model_dump(mode="json") for m in _REGISTRY.get_by_domain(domain)]


@router.get("/gap-report", response_model=MaskRegistryOut, summary="Class a gap report abrufen")
async def get_class_a_gap_report(tenant_id: str = Depends(get_tenant_id)):
    """
    Liefert Klasse-A-Masken ohne Wave-1-Contract (technische Schulden).
    Nuetzlich fuer Sprint-Planung und Architektur-Reviews.
    """
    _ = tenant_id
    gaps = _REGISTRY.class_a_without_wave1_contract()
    all_a = _REGISTRY.get_by_class(MaskClass.A)
    return {
        "class_a_total": len(all_a),
        "class_a_with_wave1_contract": len(all_a) - len(gaps),
        "class_a_gap_count": len(gaps),
        "gaps": [m.model_dump(mode="json") for m in gaps],
    }
