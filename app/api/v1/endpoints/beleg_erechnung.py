"""E-Rechnung des Belegs: XRechnung erzeugen und archivieren, archiviertes Original lesen (BELEG-052 Phase 2).

* ``POST /belege/{belegart}/{id}/actions/erechnung`` - Maskenaktion (Trockenlauf, Wiederholungsschutz, Audit): nur
  gebuchte Ausgangsrechnung/-gutschrift; das XML steht vor jeder Auslieferung im GoBD-Archiv.
* ``GET /belege/{belegart}/{id}/erechnung`` - Lesen des archivierten Originals fuer den Download (schreibt nichts).
"""
from __future__ import annotations

import base64
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.schemas.base import TypedObjectOut
from app.auth.beleg_roles import verlange
from app.auth.bereich_roles import SCHREIBEN
from app.auth.deps import get_current_user
from app.core.belegvertrag import BELEGARTEN
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.mask_action_runtime_service import MaskActionResult, run_delegated_mask_action

router = APIRouter(tags=["belege", "mask-actions"])


def _art(belegart: str) -> None:
    from app.services.beleg_erechnung import E_RECHNUNG_ARTEN

    if belegart not in BELEGARTEN or belegart not in E_RECHNUNG_ARTEN:
        raise HTTPException(status_code=404, detail="Fuer diese Belegart gibt es keine E-Rechnung")


@router.post("/belege/{belegart}/{entity_id}/actions/erechnung", response_model=MaskActionResult,
             summary="E-Rechnung (XRechnung) erzeugen und archivieren", dependencies=SCHREIBEN["BELEGE"])
async def beleg_erechnung_erzeugen(belegart: str, entity_id: str, body: dict[str, Any] = Body(default_factory=dict),
                                   db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id),
                                   nutzer: Any = Depends(get_current_user)) -> MaskActionResult:
    _art(belegart)
    verlange(nutzer, "ausstellen", belegart)

    def _beleg(session: Session, eid: str, tid: str):
        from app.api.v1.endpoints.belege import beleg_lesen

        return beleg_lesen(belegart, eid, tid, session, nutzer)

    def pruefen(session: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        from app.core.exceptions import ValidationFailedError
        from app.services.beleg_erechnung import xrechnung_eingabe

        try:
            xrechnung_eingabe(session, tid, _beleg(session, eid, tid))
        except HTTPException as exc:
            return [{"field": "_entity", "message": str(exc.detail), "severity": "blocking"}]
        except ValidationFailedError as exc:
            return [{"field": "_entity", "message": str(exc.detail if hasattr(exc, "detail") else exc),
                     "severity": "blocking"}]
        return []

    def ausfuehren(session: Session, payload: dict, eid: str, tid: str) -> str:
        from app.services.beleg_erechnung import erzeuge_und_archiviere

        akteur = nutzer.get("sub") if isinstance(nutzer, dict) else None
        dateiname, neu = erzeuge_und_archiviere(session, tid, _beleg(session, eid, tid), akteur)
        return f"{dateiname} archiviert." if neu else f"{dateiname} lag schon im Archiv."

    return await run_delegated_mask_action(
        db, action_key="erechnung", entity_type=f"beleg:{belegart}", entity_id=entity_id, tenant_id=tenant_id,
        body=body, check_fn=pruefen, delegate_fn=ausfuehren, outbox_event_type=f"beleg.{belegart}.erechnung")


@router.get("/belege/{belegart}/{entity_id}/erechnung", response_model=TypedObjectOut,
            summary="Archivierte E-Rechnung (XRechnung) lesen")
def beleg_erechnung_lesen(belegart: str, entity_id: str, db: Session = Depends(get_db),
                          tenant_id: str = Depends(get_tenant_id), nutzer: Any = Depends(get_current_user)) -> dict:
    _art(belegart)
    verlange(nutzer, "lesen", belegart)
    from app.services.beleg_erechnung import archivierte_xrechnung

    archiv = archivierte_xrechnung(db, tenant_id, entity_id)
    if not archiv:
        raise HTTPException(status_code=404, detail="Noch keine E-Rechnung archiviert")
    dateiname, inhalt = archiv
    return {"dateiname": dateiname, "xml": base64.b64encode(inhalt).decode("ascii")}
