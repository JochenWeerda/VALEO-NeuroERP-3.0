from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.zertifikate import ZertifikatTyp
from app.domains.operations.models import ZertifikatAPIEntry

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/zertifikate", tags=["zertifikate"])


def _row_to_dict(row: ZertifikatAPIEntry) -> dict:
    return {
        "zertifikat_id": row.zertifikat_id,
        "tenant_id": row.tenant_id,
        "typ": row.typ,
        "zertifizierungsstelle": row.zertifizierungsstelle,
        "gueltig_von": row.gueltig_von.date().isoformat() if row.gueltig_von else None,
        "gueltig_bis": row.gueltig_bis.date().isoformat() if row.gueltig_bis else None,
        "zertifikatsnummer": row.zertifikatsnummer,
        "status": row.status,
    }


class ZertifikatCreateRequest(BaseModel):
    tenant_id: str
    typ: str
    zertifizierungsstelle: str
    gueltig_von: str
    gueltig_bis: str
    zertifikatsnummer: Optional[str] = None


@router.post("", status_code=201, summary="Zertifikat anlegen",
    response_model=CompatFlexOut
)
def create_zertifikat(req: ZertifikatCreateRequest, db: Session = Depends(get_db)):
    import uuid
    from datetime import datetime
    gueltig_von = datetime.fromisoformat(req.gueltig_von)
    gueltig_bis = datetime.fromisoformat(req.gueltig_bis)
    now = datetime.now(tz=timezone.utc)
    if gueltig_bis.date() < date.today():
        status = "abgelaufen"
    elif (gueltig_bis.date() - date.today()).days <= 30:
        status = "ablaufend"
    else:
        status = "gueltig"
    row = ZertifikatAPIEntry(
        zertifikat_id=str(uuid.uuid4()),
        tenant_id=req.tenant_id,
        typ=req.typ,
        zertifizierungsstelle=req.zertifizierungsstelle,
        gueltig_von=gueltig_von,
        gueltig_bis=gueltig_bis,
        zertifikatsnummer=req.zertifikatsnummer,
        status=status,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _row_to_dict(row)


@router.get("/tenant/{tenant_id}", summary="By tenant abrufen",
    response_model=list[CompatFlexOut]
)
def get_by_tenant(tenant_id: str, db: Session = Depends(get_db)):
    rows = db.query(ZertifikatAPIEntry).filter(ZertifikatAPIEntry.tenant_id == tenant_id).all()
    return [_row_to_dict(r) for r in rows]


@router.get("/ablaufend", summary="Ablaufend abrufen",
    response_model=list[CompatFlexOut]
)
def get_ablaufend(tage_vorwarnung: int = Query(30), db: Session = Depends(get_db)):
    from datetime import timedelta
    deadline = datetime.now(tz=timezone.utc) + timedelta(days=tage_vorwarnung)
    today = datetime.now(tz=timezone.utc)
    rows = db.query(ZertifikatAPIEntry).filter(
        ZertifikatAPIEntry.gueltig_bis >= today,
        ZertifikatAPIEntry.gueltig_bis <= deadline,
    ).all()
    return [_row_to_dict(r) for r in rows]
