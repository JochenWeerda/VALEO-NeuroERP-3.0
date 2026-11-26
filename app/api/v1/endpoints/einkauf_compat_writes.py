"""Einkauf Angebot/Anlieferavis Write-Endpunkte (Godfile-Auslagerung aus compat)."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.bereich_roles import SCHREIBEN
from app.core.database import get_db
from app.core.exceptions import EntityNotFoundError
from app.core.tenant import get_tenant_id
from app.api.v1.schemas.mask_entity_contracts import EinkaufAngebotOut, EinkaufAnlieferavisOut
from app.services.einkauf_compat_service import EinkaufCompatService

router = APIRouter(tags=["compat", "einkauf", "parity"])

@router.post("/einkauf/angebote", response_model=EinkaufAngebotOut, status_code=201, summary="Angebot anlegen einkauf", dependencies=SCHREIBEN["EINKAUF"])
async def einkauf_angebot_create(
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return EinkaufCompatService(db, tenant_id).create_angebot(payload)


@router.put("/einkauf/angebote/{angebot_id}", response_model=EinkaufAngebotOut, summary="Angebot aktualisieren einkauf", dependencies=SCHREIBEN["EINKAUF"])
async def einkauf_angebot_update(
    angebot_id: str,
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        return EinkaufCompatService(db, tenant_id).update_angebot(angebot_id, payload)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/einkauf/anlieferavis", response_model=EinkaufAnlieferavisOut, status_code=201, summary="Anlieferavis anlegen einkauf", dependencies=SCHREIBEN["EINKAUF"])
async def einkauf_anlieferavis_create(
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return EinkaufCompatService(db, tenant_id).create_anlieferavis(payload)


@router.put("/einkauf/anlieferavis/{avis_id}", response_model=EinkaufAnlieferavisOut, summary="Anlieferavis aktualisieren einkauf", dependencies=SCHREIBEN["EINKAUF"])
async def einkauf_anlieferavis_update(
    avis_id: str,
    payload: dict[str, Any],
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        return EinkaufCompatService(db, tenant_id).update_anlieferavis(avis_id, payload)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


