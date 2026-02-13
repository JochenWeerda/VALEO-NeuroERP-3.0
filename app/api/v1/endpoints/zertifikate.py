"""Zertifikate API - DB-backed endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.models import ZertifikatEintrag

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


@router.get("", response_model=dict)
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


@router.get("/stats", response_model=dict)
async def get_zertifikate_stats(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(ZertifikatEintrag).all()
    return {
        "gueltig": sum(1 for z in items if z.status == "gueltig"),
        "ablaufend": sum(1 for z in items if z.status == "ablaufend"),
        "abgelaufen": sum(1 for z in items if z.status == "abgelaufen"),
    }
