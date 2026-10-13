"""Der gemeinsame Freigabeweg (APPROVAL-001): anfragen, entscheiden, einsehen — fuer jeden Bereich gleich.

``subject_type`` nennt den Bereich (``docflow_document``, ``finance_ap_invoice``, ``sales_credit_note``). Regel,
Funktionstrennung, Bindung an den Inhalt und Protokoll liegen in der Approval Engine; hier steht nur der Zugang.
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.beleg_roles import verlange
from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.tenant import get_tenant_id
from app.services.finance_freigabe import engine_fuer

router = APIRouter()


class FreigabeAnfrage(BaseModel):
    action: str = Field(..., pattern="^(post|reverse)$")
    reason: Optional[str] = Field(default=None, max_length=300)


class FreigabeEntscheidung(BaseModel):
    granted: bool
    note: Optional[str] = Field(default=None, max_length=300)


def _vorgang(engine: Any, subject_id: str, aktion: str = "post") -> Any:
    try:
        return engine.vorgang(subject_id, aktion)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Vorgang nicht gefunden") from exc


@router.get("/{subject_type}/{subject_id}", response_model=list[dict[str, Any]], summary="Freigaben eines Vorgangs")
def freigaben(
    subject_type: str,
    subject_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
) -> list[dict[str, Any]]:
    engine = engine_fuer(subject_type, db, tenant_id)
    verlange(nutzer, "lesen", _vorgang(engine, subject_id).belegart)
    return engine.liste(subject_id)


@router.post("/{subject_type}/{subject_id}", response_model=dict[str, Any],
             summary="Freigabe durch eine zweite Person anfragen")
def freigabe_anfragen(
    subject_type: str,
    subject_id: str,
    payload: FreigabeAnfrage,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
) -> dict[str, Any]:
    """Anfragen darf, wer die Aktion selbst ausfuehren duerfte. Der Antragsteller kommt aus der Anmeldung."""
    engine = engine_fuer(subject_type, db, tenant_id)
    belegart = _vorgang(engine, subject_id, payload.action).belegart
    verlange(nutzer, "buchen" if payload.action == "post" else "stornieren", belegart)
    antragsteller = str(nutzer.get("sub") or "").strip() if isinstance(nutzer, dict) else ""
    try:
        return engine.beantrage(subject_id, payload.action, antragsteller, payload.reason)
    except EntityNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=exc.detail)
    except (ConflictError, ValidationFailedError) as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=exc.detail)


@router.post("/{subject_type}/{subject_id}/{approval_id}/decision", response_model=dict[str, Any],
             summary="Freigabe erteilen oder ablehnen")
def freigabe_entscheiden(
    subject_type: str,
    subject_id: str,
    approval_id: str,
    payload: FreigabeEntscheidung,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    nutzer: Any = Depends(get_current_user),
) -> dict[str, Any]:
    """Recht, Funktionstrennung, Ablauf und unveraenderter Inhalt prueft die Approval Engine."""
    engine = engine_fuer(subject_type, db, tenant_id)
    try:
        return engine.entscheide(subject_id, approval_id, nutzer, payload.granted, payload.note)
    except EntityNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=exc.detail)
    except ConflictError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=exc.detail)
    except ValidationFailedError as exc:
        db.rollback()
        raise HTTPException(status_code=403, detail=exc.detail)
