"""Pruefkorb des Controllers (FIN-CONTROL-001).

Die Kontroll-Engine legt hier ab, was an ausgefuehrten Vorgaengen auffaellt: Warnungen (der Vorgang lief) und
kritische Befunde (er lief erst nach unabhaengiger Freigabe). Der Controller sieht die offenen Befunde und bewertet
sie; wer gebucht hat, prueft seinen Befund nicht selbst.
"""
from __future__ import annotations

import json
from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.beleg_roles import rollen_von
from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.tenant import get_tenant_id
from app.services import kontrollkorb
from app.services.freigabe_engine import KONTROLLROLLEN, pruefe_befund, pruefkorb
from app.api.v1.schemas.base import TypedObjectOut
from app.services.mask_action_runtime_service import MaskActionResult as MaskActionResultOut
from app.services.mask_commands import statusaktion
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)

router = APIRouter()

# Lesen darf auch die Buchhaltung: Sie soll sehen, was an ihren Vorgaengen aufgefallen ist.
_LESEN = KONTROLLROLLEN | frozenset({"FINANCE_LESEN", "FINANCE_BEARBEITEN"})


class Befundpruefung(BaseModel):
    note: str = Field(..., min_length=3, max_length=500)


@router.get("/befunde", response_model=list[TypedObjectOut], summary="Pruefkorb: Befunde der Kontroll-Engine")
def befunde(
    status: Optional[str] = Query("offen", pattern="^(offen|geprueft)$"),
    limit: int = Query(100, ge=1, le=500),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
) -> list[dict[str, Any]]:
    if not rollen_von(nutzer) & _LESEN:
        raise HTTPException(status_code=403, detail="Keine Berechtigung für den Prüfkorb.")
    return pruefkorb(db, tenant_id, status, limit)


def _nur_leser(nutzer: Any) -> None:
    if not rollen_von(nutzer) & _LESEN:
        raise HTTPException(status_code=403, detail="Keine Berechtigung für den Prüfkorb.")


@router.get("/pruefkorb", response_model=TypedObjectOut, summary="Pruefkorb: Arbeitsliste des Controllers")
def arbeitsliste(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    q: Optional[str] = Query(None, max_length=120),
    sort: Optional[str] = Query(None, max_length=40),
    sort_dir: Optional[str] = Query(None, pattern="^(asc|desc)$"),
    filter_plan: Optional[str] = Query(None, description="JSON-Spaltenfilter der Maskenlaufzeit"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
) -> dict[str, Any]:
    """Ohne Filter auf den Stand: die offenen Befunde, kritische zuerst, darin die aeltesten."""
    _nur_leser(nutzer)
    plan: dict[str, Any] = {}
    if filter_plan:
        try:
            plan = json.loads(filter_plan)
        except (ValueError, TypeError) as fehler:
            raise HTTPException(status_code=422, detail="filter_plan ist kein gültiges JSON") from fehler
        if not isinstance(plan, dict):
            raise HTTPException(status_code=422, detail="filter_plan muss ein Objekt sein")
    return kontrollkorb.seite(db, tenant_id, page=page, limit=limit, q=q, sort=sort, sort_dir=sort_dir, filter_plan=plan)


@router.get("/lagebild", response_model=TypedObjectOut, summary="Pruefkorb: Lagebild fuer den Controller")
def lage(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
) -> dict[str, Any]:
    _nur_leser(nutzer)
    return kontrollkorb.lagebild(db, tenant_id)


@router.post("/befunde/{befund_id}/pruefung", response_model=TypedObjectOut, summary="Befund als geprueft bewerten", dependencies=SCHREIBEN["CONTROLLING"])
def befund_pruefen(
    befund_id: str,
    payload: Befundpruefung,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
) -> dict[str, Any]:
    try:
        return pruefe_befund(db, tenant_id, befund_id, nutzer, payload.note)
    except EntityNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail="Befund nicht gefunden") from exc
    except ConflictError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=exc.detail) from exc
    except ValidationFailedError as exc:
        db.rollback()
        raise HTTPException(status_code=403, detail=exc.detail) from exc


@router.post(
    "/befunde/{entity_id}/actions/pruefen",
    response_model=MaskActionResultOut,
    summary="Pruefkorb: Befund bewerten (Maskenaktion)",
)
async def befund_pruefen_aktion(
    entity_id: str,
    body: dict[str, Any] = Body(default_factory=dict),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
) -> dict[str, Any]:
    """Derselbe Fachweg wie ``/pruefung``; die Bewertung (``note``) ist zugleich die Audit-Begruendung.

    Rolle, Funktionstrennung (wer gebucht hat, prueft nicht) und Person statt Dienstkonto prueft
    ``pruefe_befund`` — im Trockenlauf vorab dieselben Bedingungen.
    """
    _nur_leser(nutzer)
    note = str(body.get("note") or body.get("_auditReason") or "").strip()
    body = {**body, "_auditReason": body.get("_auditReason") or note}
    wer = str((nutzer or {}).get("sub") or "") if isinstance(nutzer, dict) else ""

    def vorpruefung(row: dict[str, Any]) -> str | None:
        if len(note) < 3:
            return "Die Pruefung braucht eine Bewertung."
        if not rollen_von(nutzer) & KONTROLLROLLEN:
            return "Keine Berechtigung fuer den Pruefkorb."
        if row.get("actor") and str(row["actor"]) == wer:
            return "Wer gebucht hat, prueft den Befund nicht selbst."
        return None

    def ausfuehren(db_: Session, _payload: dict[str, Any]) -> str:
        pruefe_befund(db_, tenant_id, entity_id, nutzer, note)
        return "Befund bewertet."

    result = await statusaktion(
        db, action_key="pruefen", entity_type="control_finding", entity_id=entity_id, tenant_id=tenant_id,
        body=body, erlaubt={"offen"}, ausfuehren=ausfuehren, zusatzpruefung=vorpruefung, begruendung_pflicht=False,
        status_sql="SELECT status, actor FROM domain_docflow.control_findings WHERE id=:id AND tenant_id=:tid",
        event_type="finance.control_finding.reviewed",
    )
    return result.model_dump()
