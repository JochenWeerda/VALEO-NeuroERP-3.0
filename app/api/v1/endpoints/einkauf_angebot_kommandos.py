"""Zeilenaktionen der Angebots-Liste als Fachaktion fuer Maske, CLI und MCP (MASK-STUDIO-ROLLOUT, Welle 1).

Die Statuswege ``/review``, ``/approve`` und ``/reject`` setzten den Status in jedem Zustand, auch ein bestelltes
Angebot wieder auf GEPRUEFT. Die handgebaute Liste grenzte das nur im Browser ein. Hier gelten die Statusgrenzen auf
dem Server, mit den Rahmenregeln von ``statusaktion`` (Trockenlauf, Wiederholung, Audit, Savepoint). Bestellen
laeuft ueber den bestehenden Weg ``/einkauf/angebote/{id}/actions/bestellen``.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.auth.bereich_roles import SCHREIBEN
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult
from app.services.mask_commands import statusaktion

router = APIRouter(tags=["mask-actions"])

_STATUS = ("SELECT upper(coalesce(status, 'ERFASST')) AS status FROM einkauf_angebote "
           "WHERE (id = :id OR angebotsnummer = :id) AND tenant_id = :tid")

#: Aktion -> (Zielstatus, erlaubte Ausgangsstatus, Begruendung Pflicht)
_UEBERGAENGE: dict[str, tuple[str, set[str], bool]] = {
    "pruefen": ("GEPRUEFT", {"ERFASST", "OFFEN", "ENTWURF"}, False),
    "genehmigen": ("GENEHMIGT", {"GEPRUEFT"}, False),
    "ablehnen": ("ABGELEHNT", {"ERFASST", "OFFEN", "ENTWURF", "GEPRUEFT", "GENEHMIGT"}, True),
}


async def _uebergang(aktion: str, entity_id: str, body: dict[str, Any], db: Session, tenant_id: str) -> MaskActionResult:
    from app.services.einkauf_compat_service import EinkaufCompatService

    ziel, erlaubt, grund = _UEBERGAENGE[aktion]

    def ausfuehren(session: Session, payload: dict[str, Any]) -> str:
        EinkaufCompatService(session, tenant_id).update_angebot_status(entity_id, ziel, ziel.lower())
        return f"Angebot {ziel.lower()}."

    return await statusaktion(
        db, action_key=aktion, entity_type="angebot", entity_id=entity_id, tenant_id=tenant_id, body=body,
        status_sql=_STATUS, erlaubt=erlaubt, ausfuehren=ausfuehren, event_type=f"einkauf.angebot.{ziel.lower()}",
        begruendung_pflicht=grund)


@router.post("/einkauf/angebote/{entity_id}/actions/pruefen", response_model=MaskActionResult,
             summary="Angebot als geprueft markieren", dependencies=SCHREIBEN["EINKAUF"])
async def angebot_pruefen(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                          db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    return await _uebergang("pruefen", entity_id, body, db, tenant_id)


@router.post("/einkauf/angebote/{entity_id}/actions/genehmigen", response_model=MaskActionResult,
             summary="Geprueftes Angebot genehmigen", dependencies=SCHREIBEN["EINKAUF"])
async def angebot_genehmigen(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                             db: Session = Depends(get_db),
                             tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    return await _uebergang("genehmigen", entity_id, body, db, tenant_id)


@router.post("/einkauf/angebote/{entity_id}/actions/ablehnen", response_model=MaskActionResult,
             summary="Angebot mit Begruendung ablehnen", dependencies=SCHREIBEN["EINKAUF"])
async def angebot_ablehnen(entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                           db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> MaskActionResult:
    return await _uebergang("ablehnen", entity_id, body, db, tenant_id)
