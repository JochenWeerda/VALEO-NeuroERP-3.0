"""Zertifikate (Bio, QS, GlobalG.A.P. ...) im Mandanten.

Bis 04.11.2026 (Batch 9) legte jeder Lesezugriff drei erfundene Zertifikate an (Seed), kein Weg kannte einen
Mandanten, und Aendern/Loeschen nahmen die Text-Kennung als Zahl an (immer 422).
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.domains.operations.models import ZertifikatEintrag

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.zertifikate_schemas import ZertifikateOut
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)


router = APIRouter(prefix="/zertifikate", tags=["Zertifikate"])


def _dt(v: Optional[datetime]) -> Optional[str]:
    return v.date().isoformat() if v else None




@router.get("", response_model=ZertifikateOut, summary="Zertifikate auflisten")
async def list_zertifikate(status: Optional[str] = Query(None, description="Filter by status"), tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    query = db.query(ZertifikatEintrag).filter(ZertifikatEintrag.tenant_id == tenant_id)
    if status:
        query = query.filter(ZertifikatEintrag.status == status)
    items = query.order_by(ZertifikatEintrag.gueltig_bis.asc()).limit(2000).all()
    return {
        "items": [
            {
                "id": i.id,
                "art": i.art,
                "standard": i.standard,
                "nummer": i.nummer,
                "gueltig_bis": _dt(i.gueltig_bis),
                "audit": _dt(i.audit),
                "status": i.status,
            }
            for i in items
        ],
        "total": len(items),
    }


@router.get("/stats", response_model=ZertifikateOut, summary="Zertifikate stats abrufen")
async def get_zertifikate_stats(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    items = db.query(ZertifikatEintrag).filter(ZertifikatEintrag.tenant_id == tenant_id).limit(10000).all()
    return {
        "gueltig": sum(1 for z in items if z.status == "gueltig"),
        "ablaufend": sum(1 for z in items if z.status == "ablaufend"),
        "abgelaufen": sum(1 for z in items if z.status == "abgelaufen"),
    }


# --------------- Pydantic Schemas ---------------
from pydantic import BaseModel
from datetime import date


class ZertifikatCreate(BaseModel):
    art: str
    standard: str
    nummer: str
    gueltig_bis: date
    audit: Optional[date] = None
    status: str = "gueltig"


class ZertifikatUpdate(BaseModel):
    art: Optional[str] = None
    standard: Optional[str] = None
    nummer: Optional[str] = None
    gueltig_bis: Optional[date] = None
    audit: Optional[date] = None
    status: Optional[str] = None


# --------------- POST / PUT / DELETE ---------------
from fastapi import HTTPException
from starlette.responses import Response


@router.post("", response_model=ZertifikateOut, status_code=201, summary="Zertifikat anlegen", dependencies=SCHREIBEN["QUALITAET"])
async def create_zertifikat(
    body: ZertifikatCreate,
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db),
) -> dict:
    """Create a new Zertifikat entry."""
    z = ZertifikatEintrag(
        tenant_id=tenant_id,
        art=body.art,
        standard=body.standard,
        nummer=body.nummer,
        gueltig_bis=datetime.combine(body.gueltig_bis, datetime.min.time()),
        audit=datetime.combine(body.audit, datetime.min.time()) if body.audit else None,
        status=body.status,
    )
    db.add(z)
    db.commit()
    db.refresh(z)
    return {
        "id": z.id,
        "art": z.art,
        "standard": z.standard,
        "nummer": z.nummer,
        "gueltig_bis": _dt(z.gueltig_bis),
        "audit": _dt(z.audit),
        "status": z.status,
    }


@router.put("/{zertifikat_id}", response_model=ZertifikateOut, summary="Zertifikat aktualisieren", dependencies=SCHREIBEN["QUALITAET"])
async def update_zertifikat(
    zertifikat_id: str,
    body: ZertifikatUpdate,
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db),
) -> dict:
    """Update an existing Zertifikat."""
    z = db.query(ZertifikatEintrag).filter(ZertifikatEintrag.tenant_id == tenant_id).filter(ZertifikatEintrag.id == zertifikat_id).first()
    if not z:
        raise HTTPException(status_code=404, detail="Zertifikat nicht gefunden")
    update_data = body.model_dump(exclude_unset=True)
    if "gueltig_bis" in update_data and update_data["gueltig_bis"] is not None:
        update_data["gueltig_bis"] = datetime.combine(update_data["gueltig_bis"], datetime.min.time())
    if "audit" in update_data and update_data["audit"] is not None:
        update_data["audit"] = datetime.combine(update_data["audit"], datetime.min.time())
    for field, value in update_data.items():
        setattr(z, field, value)
    db.commit()
    db.refresh(z)
    return {
        "id": z.id,
        "art": z.art,
        "standard": z.standard,
        "nummer": z.nummer,
        "gueltig_bis": _dt(z.gueltig_bis),
        "audit": _dt(z.audit),
        "status": z.status,
    }


@router.delete("/{zertifikat_id}", response_class=Response, status_code=204, response_model=None, summary="Zertifikat löschen", dependencies=SCHREIBEN["QUALITAET"])
async def delete_zertifikat(
    zertifikat_id: str,
    tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db),
) -> Response:
    """Soft-delete: set status to 'abgelaufen'."""
    z = db.query(ZertifikatEintrag).filter(ZertifikatEintrag.tenant_id == tenant_id).filter(ZertifikatEintrag.id == zertifikat_id).first()
    if not z:
        raise HTTPException(status_code=404, detail="Zertifikat nicht gefunden")
    z.status = "abgelaufen"
    db.commit()
    return Response(status_code=204)
