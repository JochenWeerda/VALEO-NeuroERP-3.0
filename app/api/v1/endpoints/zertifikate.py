"""Zertifikate API - DB-backed endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.models import ZertifikatEintrag

from app.api.v1.schemas.base import BaseSchema


router = APIRouter(prefix="/zertifikate", tags=["Zertifikate"])


def _dt(v: Optional[datetime]) -> Optional[str]:
    return v.date().isoformat() if v else None


def _seed(db: Session) -> None:
    if db.query(ZertifikatEintrag).count() > 0:
        return
    db.add_all(
        [
            ZertifikatEintrag(
                art="Bio-Zertifikat",
                standard="EU-Bio-Verordnung",
                nummer="BIO-2025-1234",
                gueltig_bis=datetime(2026, 12, 31),
                audit=datetime(2026, 2, 15),
                status="gueltig",
            ),
            ZertifikatEintrag(
                art="QS-Zertifikat",
                standard="QS-GAP",
                nummer="QS-2025-5678",
                gueltig_bis=datetime(2026, 6, 30),
                audit=datetime(2025, 12, 1),
                status="gueltig",
            ),
            ZertifikatEintrag(
                art="GlobalG.A.P.",
                standard="GGN",
                nummer="GGN-12345678",
                gueltig_bis=datetime(2025, 9, 30),
                audit=datetime(2025, 8, 15),
                status="ablaufend",
            ),
        ]
    )
    db.commit()


@router.get("", response_model=CompatFlexOut, summary="Zertifikate auflisten")
async def list_zertifikate(status: Optional[str] = Query(None, description="Filter by status"), db: Session = Depends(get_db)) -> dict:
    _seed(db)
    query = db.query(ZertifikatEintrag)
    if status:
        query = query.filter(ZertifikatEintrag.status == status)
    items = query.order_by(ZertifikatEintrag.gueltig_bis.asc()).all()
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


@router.get("/stats", response_model=CompatFlexOut, summary="Zertifikate stats abrufen")
async def get_zertifikate_stats(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(ZertifikatEintrag).all()
    return {
        "gueltig": sum(1 for z in items if z.status == "gueltig"),
        "ablaufend": sum(1 for z in items if z.status == "ablaufend"),
        "abgelaufen": sum(1 for z in items if z.status == "abgelaufen"),
    }


# --------------- Pydantic Schemas ---------------
from pydantic import BaseModel
from app.api.v1.schemas.base import CompatFlexOut
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


@router.post("", response_model=CompatFlexOut, status_code=201, summary="Zertifikat anlegen")
async def create_zertifikat(
    body: ZertifikatCreate,
    db: Session = Depends(get_db),
) -> dict:
    """Create a new Zertifikat entry."""
    z = ZertifikatEintrag(
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


@router.put("/{zertifikat_id}", response_model=CompatFlexOut, summary="Zertifikat aktualisieren")
async def update_zertifikat(
    zertifikat_id: int,
    body: ZertifikatUpdate,
    db: Session = Depends(get_db),
) -> dict:
    """Update an existing Zertifikat."""
    z = db.query(ZertifikatEintrag).filter(ZertifikatEintrag.id == zertifikat_id).first()
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


@router.delete("/{zertifikat_id}", response_class=Response, status_code=204, response_model=None, summary="Zertifikat löschen")
async def delete_zertifikat(
    zertifikat_id: int,
    db: Session = Depends(get_db),
) -> Response:
    """Soft-delete: set status to 'abgelaufen'."""
    z = db.query(ZertifikatEintrag).filter(ZertifikatEintrag.id == zertifikat_id).first()
    if not z:
        raise HTTPException(status_code=404, detail="Zertifikat nicht gefunden")
    z.status = "abgelaufen"
    db.commit()
    return Response(status_code=204)
