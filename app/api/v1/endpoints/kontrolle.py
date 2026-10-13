"""Pruefkorb des Controllers (FIN-CONTROL-001).

Die Kontroll-Engine legt hier ab, was an ausgefuehrten Vorgaengen auffaellt: Warnungen (der Vorgang lief) und
kritische Befunde (er lief erst nach unabhaengiger Freigabe). Der Controller sieht die offenen Befunde und bewertet
sie; wer gebucht hat, prueft seinen Befund nicht selbst.
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.beleg_roles import rollen_von
from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.tenant import get_tenant_id
from app.services.freigabe_engine import KONTROLLROLLEN, pruefe_befund, pruefkorb

router = APIRouter()

# Lesen darf auch die Buchhaltung: Sie soll sehen, was an ihren Vorgaengen aufgefallen ist.
_LESEN = KONTROLLROLLEN | frozenset({"FINANCE_LESEN", "FINANCE_BEARBEITEN", "manager"})


class Befundpruefung(BaseModel):
    note: str = Field(..., min_length=3, max_length=500)


@router.get("/befunde", response_model=list[dict[str, Any]], summary="Pruefkorb: Befunde der Kontroll-Engine")
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


@router.post("/befunde/{befund_id}/pruefung", response_model=dict[str, Any], summary="Befund als geprueft bewerten")
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
