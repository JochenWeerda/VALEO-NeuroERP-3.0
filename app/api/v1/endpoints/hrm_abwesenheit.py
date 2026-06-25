"""HRM-ABWESENHEIT-ANTRAG-001 — Abwesenheitsantrag API."""
from __future__ import annotations

from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel

from app.services.hrm_abwesenheit_service import (
    AbwesenheitKonfliktError,
    AbwesenheitStatus,
    AbwesenheitTyp,
    AntragNichtGefundenError,
    UngueltigerStatusUebergangError,
    get_abwesenheit_service,
)

router = APIRouter(prefix="/personal/abwesenheit", tags=["hrm", "abwesenheit"])


def _tenant(x_tenant_id: Annotated[str | None, Header()] = None) -> str:
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID fehlt")
    return x_tenant_id


class AntragCreate(BaseModel):
    mitarbeiter_nr: str
    typ: str
    von_datum: date
    bis_datum: date
    beantragt_von: str
    kommentar: str | None = None
    vertretung_durch: str | None = None


class GenehmigenBody(BaseModel):
    genehmigt_von: str
    kommentar: str | None = None


class AblehnenBody(BaseModel):
    abgelehnt_von: str
    grund: str


class ZurueckziehenBody(BaseModel):
    mitarbeiter_nr: str


@router.post(
    "/antraege",
    response_model=dict[str, Any],
    status_code=201,
    summary="Abwesenheitsantrag stellen",
)
def antrag_stellen(body: AntragCreate, x_tenant_id: Annotated[str | None, Header()] = None) -> dict[str, Any]:
    tid = _tenant(x_tenant_id)
    svc = get_abwesenheit_service(tid)
    try:
        antrag = svc.antrag_stellen(
            mitarbeiter_nr=body.mitarbeiter_nr,
            typ=AbwesenheitTyp(body.typ),
            von_datum=body.von_datum,
            bis_datum=body.bis_datum,
            beantragt_von=body.beantragt_von,
            kommentar=body.kommentar,
            vertretung_durch=body.vertretung_durch,
        )
    except AbwesenheitKonfliktError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return antrag.to_dict()


@router.get(
    "/antraege",
    response_model=dict[str, Any],
    summary="Abwesenheitsantraege listen",
)
def list_antraege(
    mitarbeiter_nr: str | None = Query(None),
    status: str | None = Query(None),
    typ: str | None = Query(None),
    von_ab: date | None = Query(None),
    x_tenant_id: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    tid = _tenant(x_tenant_id)
    svc = get_abwesenheit_service(tid)
    items = svc.list_antraege(
        mitarbeiter_nr=mitarbeiter_nr,
        status=AbwesenheitStatus(status) if status else None,
        typ=AbwesenheitTyp(typ) if typ else None,
        von_ab=von_ab,
    )
    return {"items": [a.to_dict() for a in items], "count": len(items)}


@router.get(
    "/antraege/{antrag_id}",
    response_model=dict[str, Any],
    summary="Abwesenheitsantrag abrufen",
)
def get_antrag(antrag_id: str, x_tenant_id: Annotated[str | None, Header()] = None) -> dict[str, Any]:
    tid = _tenant(x_tenant_id)
    svc = get_abwesenheit_service(tid)
    try:
        return svc.get(antrag_id).to_dict()
    except AntragNichtGefundenError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post(
    "/antraege/{antrag_id}/genehmigen",
    response_model=dict[str, Any],
    summary="Abwesenheitsantrag genehmigen",
)
def genehmigen(
    antrag_id: str, body: GenehmigenBody, x_tenant_id: Annotated[str | None, Header()] = None
) -> dict[str, Any]:
    tid = _tenant(x_tenant_id)
    svc = get_abwesenheit_service(tid)
    try:
        return svc.genehmigen(antrag_id, genehmigt_von=body.genehmigt_von, kommentar=body.kommentar).to_dict()
    except AntragNichtGefundenError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except UngueltigerStatusUebergangError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@router.post(
    "/antraege/{antrag_id}/ablehnen",
    response_model=dict[str, Any],
    summary="Abwesenheitsantrag ablehnen",
)
def ablehnen(
    antrag_id: str, body: AblehnenBody, x_tenant_id: Annotated[str | None, Header()] = None
) -> dict[str, Any]:
    tid = _tenant(x_tenant_id)
    svc = get_abwesenheit_service(tid)
    try:
        return svc.ablehnen(antrag_id, abgelehnt_von=body.abgelehnt_von, grund=body.grund).to_dict()
    except AntragNichtGefundenError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except (UngueltigerStatusUebergangError, ValueError) as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@router.post(
    "/antraege/{antrag_id}/zurueckziehen",
    response_model=dict[str, Any],
    summary="Abwesenheitsantrag zurueckziehen",
)
def zurueckziehen(
    antrag_id: str, body: ZurueckziehenBody, x_tenant_id: Annotated[str | None, Header()] = None
) -> dict[str, Any]:
    tid = _tenant(x_tenant_id)
    svc = get_abwesenheit_service(tid)
    try:
        return svc.zurueckziehen(antrag_id, mitarbeiter_nr=body.mitarbeiter_nr).to_dict()
    except AntragNichtGefundenError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except (UngueltigerStatusUebergangError, PermissionError) as e:
        raise HTTPException(status_code=409, detail=str(e)) from e


@router.get(
    "/urlaubskonto/{mitarbeiter_nr}",
    response_model=dict[str, Any],
    summary="Urlaubskonto abrufen",
)
def urlaubskonto(
    mitarbeiter_nr: str,
    jahr: int = Query(..., ge=2020, le=2050),
    x_tenant_id: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    tid = _tenant(x_tenant_id)
    svc = get_abwesenheit_service(tid)
    return svc.urlaubskonto(mitarbeiter_nr, jahr)
