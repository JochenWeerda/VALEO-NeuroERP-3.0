"""
Annahme — Eingangs-Warteschlange (Ernte-Annahme / Wareneingang)

GET  /annahme/warteschlange          Liste der wartenden Anlieferungen
POST /annahme/warteschlange          Neue Anlieferung in Warteschlange
POST /annahme/warteschlange/{id}/repair-article  Artikel-Nummer reparieren
"""
from __future__ import annotations

from typing import Any, Optional
from fastapi import APIRouter, Depends, Path, Body

from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/annahme", tags=["annahme", "warteschlange"])


@router.get("/warteschlange", summary="Annahme-Warteschlange abrufen")
async def list_warteschlange(
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    """Stub: Gibt die aktuelle Eingangs-Warteschlange zurück."""
    return []


@router.post("/warteschlange", status_code=201, summary="Anlieferung in Warteschlange aufnehmen")
async def create_warteschlange_entry(
    body: dict[str, Any] = Body(default={}),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Stub: Nimmt eine neue Anlieferung in die Warteschlange auf."""
    return {"id": "stub", "status": "wartend", **body}


@router.post("/warteschlange/{entry_id}/repair-article", summary="Artikel-Nummer reparieren")
async def repair_article(
    entry_id: str = Path(...),
    body: dict[str, Any] = Body(default={}),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Stub: Korrigiert die Artikel-Nr. eines Warteschlangen-Eintrags."""
    return {"id": entry_id, "repaired": True, **body}
