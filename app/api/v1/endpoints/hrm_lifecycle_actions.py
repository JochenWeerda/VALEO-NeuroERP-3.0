"""DOM-HRM-004 — HRM Lifecycle: Zeiterfassung, Abwesenheit, Arbeitszeitkonto."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app.core.database import get_db

router = APIRouter(prefix="/hrm/lifecycle", tags=["hrm-lifecycle"])
logger = logging.getLogger(__name__)


class ZeitbuchungCreateRequest(BaseModel):
    mitarbeiter_id: str
    datum: str
    von_zeit: str
    bis_zeit: str
    taetigkeit: str
    kostenstelle_id: str
    operator: str = "system"


class ZeitbuchungTransitionRequest(BaseModel):
    new_status: str
    operator: str = "system"
    korrektur_grund: str = ""


class AbwesenheitCreateRequest(BaseModel):
    mitarbeiter_id: str
    abwesenheit_typ: str
    von_datum: str
    bis_datum: str
    arbeitstage: int
    kommentar: str = ""
    operator: str = "system"


class AbwesenheitTransitionRequest(BaseModel):
    new_status: str
    operator: str = "system"
    ablehnungs_grund: str = ""


@router.post("/zeitbuchungen", response_model=Dict[str, Any])
def create_zeitbuchung(
    req: ZeitbuchungCreateRequest,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.hrm_zeiterfassung_service import (
        create_zeitbuchung as svc,
        ZeiterfassungError,
    )
    try:
        return svc(
            db=db,
            tenant_id=x_tenant_id,
            mitarbeiter_id=req.mitarbeiter_id,
            datum=req.datum,
            von_zeit=req.von_zeit,
            bis_zeit=req.bis_zeit,
            taetigkeit=req.taetigkeit,
            kostenstelle_id=req.kostenstelle_id,
            operator=req.operator,
        )
    except ZeiterfassungError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/zeitbuchungen/{buchung_id}/transition", response_model=Dict[str, Any])
def transition_zeitbuchung(
    buchung_id: str,
    req: ZeitbuchungTransitionRequest,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.hrm_zeiterfassung_service import (
        transition_zeitbuchung as svc,
        ZeiterfassungError,
    )
    try:
        return svc(
            db=db,
            buchung_id=buchung_id,
            new_status=req.new_status,
            tenant_id=x_tenant_id,
            operator=req.operator,
            korrektur_grund=req.korrektur_grund,
        )
    except ZeiterfassungError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/arbeitszeitkonto/{mitarbeiter_id}", response_model=Dict[str, Any])
def get_arbeitszeitkonto(
    mitarbeiter_id: str,
    monat: str,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.hrm_zeiterfassung_service import get_arbeitszeitkonto as svc
    return svc(db=db, mitarbeiter_id=mitarbeiter_id, tenant_id=x_tenant_id, monat=monat)


@router.post("/abwesenheiten", response_model=Dict[str, Any])
def create_abwesenheit(
    req: AbwesenheitCreateRequest,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.hrm_abwesenheit_service import (
        create_abwesenheitsantrag as svc,
        AbwesenheitError,
    )
    try:
        return svc(
            db=db,
            tenant_id=x_tenant_id,
            mitarbeiter_id=req.mitarbeiter_id,
            abwesenheit_typ=req.abwesenheit_typ,
            von_datum=req.von_datum,
            bis_datum=req.bis_datum,
            arbeitstage=req.arbeitstage,
            kommentar=req.kommentar,
            operator=req.operator,
        )
    except AbwesenheitError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/abwesenheiten/{abwesenheit_id}/transition", response_model=Dict[str, Any])
def transition_abwesenheit(
    abwesenheit_id: str,
    req: AbwesenheitTransitionRequest,
    x_tenant_id: str = Header(...),
    db=Depends(get_db),
):
    from app.services.hrm_abwesenheit_service import (
        transition_abwesenheit as svc,
        AbwesenheitError,
    )
    try:
        return svc(
            db=db,
            abwesenheit_id=abwesenheit_id,
            new_status=req.new_status,
            tenant_id=x_tenant_id,
            operator=req.operator,
            ablehnungs_grund=req.ablehnungs_grund,
        )
    except AbwesenheitError as e:
        raise HTTPException(status_code=400, detail=str(e))
