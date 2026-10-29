"""Zeilenaktionen der Anlieferavis-Liste als Fachaktion fuer Maske, CLI und MCP (MASK-STUDIO-ROLLOUT, Welle 1).

Der Weg ``/einkauf/anlieferavis/{id}/{action}`` setzte den Status in jedem Zustand, auch ein erhaltenes Avis auf
STORNIERT. Hier gelten die Statusgrenzen auf dem Server, mit den Rahmenregeln von ``statusaktion`` (Trockenlauf,
Wiederholung, Audit, Savepoint). Der Wareneingang laeuft ueber ``/einkauf/anlieferavis/{id}/actions/wareneingang``.
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

_STATUS = ("SELECT upper(coalesce(status, 'OFFEN')) AS status FROM einkauf_anlieferavis "
           "WHERE (id = :id OR avis_nummer = :id) AND tenant_id = :tid")

#: Aktion -> (Zielstatus, erlaubte Ausgangsstatus, Begruendung Pflicht)
_UEBERGAENGE: dict[str, tuple[str, set[str], bool]] = {
    "senden": ("GESENDET", {"OFFEN", "ANGEKUENDIGT"}, False),
    "bestaetigen": ("BESTAETIGT", {"OFFEN", "ANGEKUENDIGT", "GESENDET"}, False),
    "stornieren": ("STORNIERT", {"OFFEN", "ANGEKUENDIGT", "GESENDET", "BESTAETIGT"}, True),
}


async def _uebergang(aktion: str, entity_id: str, body: dict[str, Any], db: Session, tenant_id: str) -> MaskActionResult:
    ziel, erlaubt, grund = _UEBERGAENGE[aktion]

    def ausfuehren(session: Session, payload: dict[str, Any]) -> str:
        session.execute(text("UPDATE einkauf_anlieferavis SET status = :s, updated_at = NOW() "
                             "WHERE (id = :id OR avis_nummer = :id) AND tenant_id = :tid"),
                        {"s": ziel, "id": entity_id, "tid": tenant_id})
        return f"Anlieferavis {ziel.lower()}."

    return await statusaktion(
        db, action_key=aktion, entity_type="anlieferavis", entity_id=entity_id, tenant_id=tenant_id, body=body,
        status_sql=_STATUS, erlaubt=erlaubt, ausfuehren=ausfuehren,
        event_type=f"einkauf.anlieferavis.{ziel.lower()}", begruendung_pflicht=grund)


@router.post("/einkauf/anlieferavis/{entity_id}/actions/senden", response_model=MaskActionResult,
             summary="Anlieferavis als gesendet fuehren", dependencies=SCHREIBEN["EINKAUF"])
async def avis_senden(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                      db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    return await _uebergang("senden", entity_id, body, db, tenant_id)


@router.post("/einkauf/anlieferavis/{entity_id}/actions/bestaetigen", response_model=MaskActionResult,
             summary="Anlieferavis bestaetigen", dependencies=SCHREIBEN["EINKAUF"])
async def avis_bestaetigen(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                           db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    return await _uebergang("bestaetigen", entity_id, body, db, tenant_id)


@router.post("/einkauf/anlieferavis/{entity_id}/actions/stornieren", response_model=MaskActionResult,
             summary="Anlieferavis mit Begruendung stornieren", dependencies=SCHREIBEN["EINKAUF"])
async def avis_stornieren(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                          db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    return await _uebergang("stornieren", entity_id, body, db, tenant_id)
