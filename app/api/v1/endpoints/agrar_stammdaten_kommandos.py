"""Zeilenaktionen der Agrar-Stammdatenlisten als Fachaktion fuer Maske, CLI und MCP (MASK-STUDIO-ROLLOUT, Welle 1).

Deaktivieren ist im Fachweg ``DELETE /agrar/duenger/{id}`` ein weiches Loeschen (``ist_aktiv = false``). Hier mit
Begruendung, Audit, Trockenlauf und Wiederholungsschutz von ``statusaktion``; ein schon inaktiver Duenger wird
abgewiesen statt still erneut "geloescht".
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth.bereich_roles import SCHREIBEN
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult
from app.services.mask_commands import statusaktion

router = APIRouter(tags=["mask-actions"])

_DUENGER_STATUS = ("SELECT CASE WHEN coalesce(ist_aktiv, true) THEN 'AKTIV' ELSE 'INAKTIV' END AS status "
                   "FROM domain_agrar.agrar_duenger WHERE id = :id AND tenant_id = :tid")


@router.post("/agrar/duenger/{entity_id}/actions/deaktivieren", response_model=MaskActionResult,
             summary="Duenger mit Begruendung deaktivieren", dependencies=SCHREIBEN["AGRAR"])
async def duenger_deaktivieren(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                               db: Session = Depends(get_db),
                               tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    def ausfuehren(session: Session, payload: dict[str, Any]) -> str:
        session.execute(text("UPDATE domain_agrar.agrar_duenger SET ist_aktiv = false, updated_at = now() "
                             "WHERE id = :id AND tenant_id = :tid"), {"id": entity_id, "tid": tenant_id})
        return "Duenger deaktiviert."

    return await statusaktion(
        db, action_key="deaktivieren", entity_type="duenger", entity_id=entity_id, tenant_id=tenant_id, body=body,
        status_sql=_DUENGER_STATUS, erlaubt={"AKTIV"}, ausfuehren=ausfuehren, event_type="agrar.duenger.deaktiviert",
        begruendung_pflicht=True)
