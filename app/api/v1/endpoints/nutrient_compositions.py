"""Nutrient Composition (Düngemittel-Zusammensetzung) management endpoints."""

from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ....core.config import settings
from ....core.database import get_db
from ....infrastructure.models import NutrientComposition
from ..schemas.base import PaginatedResponse

router = APIRouter()

DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


def _to_schema(row: NutrientComposition) -> dict:
    return {
        "id": str(row.id),
        "tenant_id": str(row.tenant_id),
        "lfd_nr": row.lfd_nr,
        "bezeichnung": row.bezeichnung,
        "beschreibung": row.beschreibung,
        "stickstoff_gesamt": float(row.stickstoff_gesamt) if row.stickstoff_gesamt else None,
        "ts_gehalt": float(row.ts_gehalt) if row.ts_gehalt else None,
        "n_anteil": float(row.n_anteil) if row.n_anteil else None,
        "ammonium_n": float(row.ammonium_n) if row.ammonium_n else None,
        "phosphat_p2o5": float(row.phosphat_p2o5) if row.phosphat_p2o5 else None,
        "kalium_k2o": float(row.kalium_k2o) if row.kalium_k2o else None,
        "magnesium_mgo": float(row.magnesium_mgo) if row.magnesium_mgo else None,
        "calcium_cao": float(row.calcium_cao) if row.calcium_cao else None,
        "schwefel_s": float(row.schwefel_s) if row.schwefel_s else None,
        "natrium_na2o": float(row.natrium_na2o) if row.natrium_na2o else None,
        "basis": row.basis,
        "wirtschaftsduenger": row.wirtschaftsduenger,
        "composition_type": row.composition_type,
        "laborwert_id": row.laborwert_id,
        "laborwert_name": row.laborwert_name,
        "is_active": row.is_active,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


@router.get("/", response_model=PaginatedResponse[dict], summary="Nutrient compositions auflisten")
async def list_nutrient_compositions(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    search: Optional[str] = Query(None, description="Search in name/number"),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Return a paginated list of nutrient compositions."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    query = db.query(NutrientComposition).filter(
        NutrientComposition.tenant_id == effective_tenant,
        NutrientComposition.is_active == True
    )

    if search:
        like = f"%{search}%"
        query = query.filter(
            (NutrientComposition.bezeichnung.ilike(like)) |
            (NutrientComposition.lfd_nr.ilike(like))
        )

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit if total else 1

    return PaginatedResponse[dict](
        items=[_to_schema(item) for item in items],
        total=total,
        page=page,
        size=limit,
        pages=pages,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/search", response_model=list[dict], summary="Nutrient compositions suchen")
async def search_nutrient_compositions(
    q: str = Query(..., min_length=1, description="Search term"),
    limit: int = Query(10, ge=1, le=50),
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Lightweight search for autocomplete."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    like = f"%{q}%"

    items = db.query(NutrientComposition).filter(
        NutrientComposition.tenant_id == effective_tenant,
        NutrientComposition.is_active == True,
        (NutrientComposition.bezeichnung.ilike(like)) |
        (NutrientComposition.lfd_nr.ilike(like))
    ).limit(limit).all()

    return [_to_schema(item) for item in items]


@router.get("/{composition_id}", response_model=dict, summary="Nutrient composition abrufen")
async def get_nutrient_composition(
    composition_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get a single nutrient composition by ID."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    item = db.query(NutrientComposition).filter(
        NutrientComposition.id == composition_id,
        NutrientComposition.tenant_id == effective_tenant,
        NutrientComposition.is_active == True
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Nutrient composition not found")

    return _to_schema(item)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED, summary="Nutrient composition anlegen")
async def create_nutrient_composition(
    data: dict,
    db: Session = Depends(get_db),
):
    """Create a new nutrient composition."""
    tenant_id = data.get("tenant_id", DEFAULT_TENANT)

    # Check for duplicate lfd_nr
    if data.get("lfd_nr"):
        existing = db.query(NutrientComposition).filter(
            NutrientComposition.tenant_id == tenant_id,
            NutrientComposition.lfd_nr == data["lfd_nr"],
            NutrientComposition.is_active == True
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail="Composition number already exists")

    item = NutrientComposition(
        id=str(uuid4()),
        tenant_id=tenant_id,
        lfd_nr=data.get("lfd_nr"),
        bezeichnung=data["bezeichnung"],
        beschreibung=data.get("beschreibung"),
        stickstoff_gesamt=data.get("stickstoff_gesamt"),
        ts_gehalt=data.get("ts_gehalt"),
        n_anteil=data.get("n_anteil"),
        ammonium_n=data.get("ammonium_n"),
        phosphat_p2o5=data.get("phosphat_p2o5"),
        kalium_k2o=data.get("kalium_k2o"),
        magnesium_mgo=data.get("magnesium_mgo"),
        calcium_cao=data.get("calcium_cao"),
        schwefel_s=data.get("schwefel_s"),
        natrium_na2o=data.get("natrium_na2o"),
        basis=data.get("basis"),
        wirtschaftsduenger=data.get("wirtschaftsduenger", False),
        composition_type=data.get("composition_type"),
        laborwert_id=data.get("laborwert_id"),
        laborwert_name=data.get("laborwert_name"),
        is_active=True,
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return _to_schema(item)


@router.put("/{composition_id}", response_model=dict, summary="Nutrient composition aktualisieren")
async def update_nutrient_composition(
    composition_id: str,
    data: dict,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Update a nutrient composition."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    item = db.query(NutrientComposition).filter(
        NutrientComposition.id == composition_id,
        NutrientComposition.tenant_id == effective_tenant
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Nutrient composition not found")

    # Update fields
    if "lfd_nr" in data:
        item.lfd_nr = data["lfd_nr"]
    if "bezeichnung" in data:
        item.bezeichnung = data["bezeichnung"]
    if "beschreibung" in data:
        item.beschreibung = data["beschreibung"]
    if "stickstoff_gesamt" in data:
        item.stickstoff_gesamt = data["stickstoff_gesamt"]
    if "ts_gehalt" in data:
        item.ts_gehalt = data["ts_gehalt"]
    if "n_anteil" in data:
        item.n_anteil = data["n_anteil"]
    if "ammonium_n" in data:
        item.ammonium_n = data["ammonium_n"]
    if "phosphat_p2o5" in data:
        item.phosphat_p2o5 = data["phosphat_p2o5"]
    if "kalium_k2o" in data:
        item.kalium_k2o = data["kalium_k2o"]
    if "magnesium_mgo" in data:
        item.magnesium_mgo = data["magnesium_mgo"]
    if "calcium_cao" in data:
        item.calcium_cao = data["calcium_cao"]
    if "schwefel_s" in data:
        item.schwefel_s = data["schwefel_s"]
    if "natrium_na2o" in data:
        item.natrium_na2o = data["natrium_na2o"]
    if "basis" in data:
        item.basis = data["basis"]
    if "wirtschaftsduenger" in data:
        item.wirtschaftsduenger = data["wirtschaftsduenger"]
    if "composition_type" in data:
        item.composition_type = data["composition_type"]
    if "laborwert_id" in data:
        item.laborwert_id = data["laborwert_id"]
    if "laborwert_name" in data:
        item.laborwert_name = data["laborwert_name"]
    if "is_active" in data:
        item.is_active = data["is_active"]

    db.commit()
    db.refresh(item)

    return _to_schema(item)


@router.delete("/{composition_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Nutrient composition löschen",
    response_model=None
)
async def delete_nutrient_composition(
    composition_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Soft-delete a nutrient composition."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    item = db.query(NutrientComposition).filter(
        NutrientComposition.id == composition_id,
        NutrientComposition.tenant_id == effective_tenant
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Nutrient composition not found")

    # Soft delete
    item.is_active = False
    db.commit()

    return None
