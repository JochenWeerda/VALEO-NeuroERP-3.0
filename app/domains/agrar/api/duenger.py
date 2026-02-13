"""
Dünger API endpoints
Full CRUD for Dünger-Stammdaten management
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from ....core.database import get_db
from ....infrastructure.models import Duenger as DuengerModel
from ....api.v1.schemas.base import PaginatedResponse
from ....api.v1.schemas.agrar import Duenger, DuengerCreate, DuengerUpdate

router = APIRouter()

DEFAULT_TENANT = "system"


@router.get("/", response_model=PaginatedResponse[Duenger])
async def list_duenger(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    search: Optional[str] = Query(None, description="Search in name, article number, manufacturer"),
    typ: Optional[str] = Query(None, description="Filter by type"),
    hersteller: Optional[str] = Query(None, description="Filter by manufacturer"),
    kultur_typ: Optional[str] = Query(None, description="Filter by crop type"),
    ist_aktiv: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(25, ge=1, le=200, description="Maximum number of records"),
    db: Session = Depends(get_db),
):
    """Return a paginated list of Dünger."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    query = db.query(DuengerModel).filter(DuengerModel.tenant_id == effective_tenant)

    if ist_aktiv is not None:
        query = query.filter(DuengerModel.ist_aktiv == ist_aktiv)

    if typ:
        query = query.filter(DuengerModel.typ == typ)

    if hersteller:
        query = query.filter(DuengerModel.hersteller == hersteller)

    if kultur_typ:
        query = query.filter(DuengerModel.kultur_typ == kultur_typ)

    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                DuengerModel.name.ilike(like),
                DuengerModel.artikelnummer.ilike(like),
                DuengerModel.hersteller.ilike(like),
            )
        )

    total = query.count()
    items = query.order_by(desc(DuengerModel.created_at)).offset(skip).limit(limit).all()

    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit if total else 1

    return PaginatedResponse(
        items=[Duenger.model_validate(item) for item in items],
        total=total,
        page=page,
        pages=pages,
        size=limit,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/{duenger_id}", response_model=Duenger)
async def get_duenger(
    duenger_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get a single Dünger by ID."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    duenger = (
        db.query(DuengerModel)
        .filter(
            DuengerModel.id == duenger_id,
            DuengerModel.tenant_id == effective_tenant
        )
        .first()
    )

    if not duenger:
        raise HTTPException(status_code=404, detail="Dünger not found")

    return Duenger.model_validate(duenger)


@router.post("/", response_model=Duenger, status_code=201)
async def create_duenger(
    duenger_data: DuengerCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Create a new Dünger."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    # Check if artikelnummer already exists
    existing = (
        db.query(DuengerModel)
        .filter(
            DuengerModel.artikelnummer == duenger_data.artikelnummer,
            DuengerModel.tenant_id == effective_tenant
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Dünger with article number {duenger_data.artikelnummer} already exists"
        )

    # Validate business rules
    if duenger_data.ablauf_zulassung and duenger_data.ablauf_zulassung < datetime.utcnow().date():
        raise HTTPException(
            status_code=400,
            detail="Approval expiry date cannot be in the past"
        )

    # Validate NPK values
    if any(val < 0 or val > 100 for val in [
        duenger_data.n_gehalt or 0,
        duenger_data.p_gehalt or 0,
        duenger_data.k_gehalt or 0,
        duenger_data.s_gehalt or 0,
        duenger_data.mg_gehalt or 0
    ]):
        raise HTTPException(
            status_code=400,
            detail="NPK values must be between 0 and 100"
        )

    duenger = DuengerModel(
        **duenger_data.model_dump(),
        tenant_id=effective_tenant
    )

    db.add(duenger)
    db.commit()
    db.refresh(duenger)

    return Duenger.model_validate(duenger)


@router.put("/{duenger_id}", response_model=Duenger)
async def update_duenger(
    duenger_id: str,
    duenger_data: DuengerUpdate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Update an existing Dünger."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    duenger = (
        db.query(DuengerModel)
        .filter(
            DuengerModel.id == duenger_id,
            DuengerModel.tenant_id == effective_tenant
        )
        .first()
    )

    if not duenger:
        raise HTTPException(status_code=404, detail="Dünger not found")

    update_data = duenger_data.model_dump(exclude_unset=True)

    # Validate artikelnummer uniqueness if changed
    if "artikelnummer" in update_data and update_data["artikelnummer"] != duenger.artikelnummer:
        existing = (
            db.query(DuengerModel)
            .filter(
                DuengerModel.artikelnummer == update_data["artikelnummer"],
                DuengerModel.tenant_id == effective_tenant,
                DuengerModel.id != duenger_id
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Dünger with article number {update_data['artikelnummer']} already exists"
            )

    # Validate approval expiry
    if "ablauf_zulassung" in update_data and update_data["ablauf_zulassung"]:
        from datetime import datetime
        if update_data["ablauf_zulassung"] < datetime.utcnow().date():
            raise HTTPException(
                status_code=400,
                detail="Approval expiry date cannot be in the past"
            )

    # Validate NPK values
    npk_fields = ['n_gehalt', 'p_gehalt', 'k_gehalt', 's_gehalt', 'mg_gehalt']
    for field in npk_fields:
        if field in update_data and (update_data[field] < 0 or update_data[field] > 100):
            raise HTTPException(
                status_code=400,
                detail=f"{field} must be between 0 and 100"
            )

    for key, value in update_data.items():
        setattr(duenger, key, value)

    db.commit()
    db.refresh(duenger)

    return Duenger.model_validate(duenger)


@router.delete("/{duenger_id}", status_code=204)
async def delete_duenger(
    duenger_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Delete a Dünger (soft delete)."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    duenger = (
        db.query(DuengerModel)
        .filter(
            DuengerModel.id == duenger_id,
            DuengerModel.tenant_id == effective_tenant
        )
        .first()
    )

    if not duenger:
        raise HTTPException(status_code=404, detail="Dünger not found")

    duenger.ist_aktiv = False
    db.commit()

    return None


@router.get("/search", response_model=list[Duenger])
async def search_duenger(
    q: str = Query(..., min_length=2, description="Search term"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Lightweight search endpoint for Dünger."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    like = f"%{q}%"

    query = (
        db.query(DuengerModel)
        .filter(DuengerModel.ist_aktiv == True)
        .filter(DuengerModel.tenant_id == effective_tenant)
        .filter(
            or_(
                DuengerModel.name.ilike(like),
                DuengerModel.artikelnummer.ilike(like),
                DuengerModel.hersteller.ilike(like),
            )
        )
        .order_by(DuengerModel.name.asc())
        .limit(limit)
    )

    return [Duenger.model_validate(item) for item in query.all()]


@router.get("/stats/overview")
async def get_duenger_stats(
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get Dünger statistics overview."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    # Count by type
    type_stats = {}
    types = db.query(DuengerModel.typ, db.func.count(DuengerModel.id)).filter(
        DuengerModel.tenant_id == effective_tenant,
        DuengerModel.ist_aktiv == True
    ).group_by(DuengerModel.typ).all()

    for typ, count in types:
        type_stats[typ or "Unbekannt"] = count

    # Safety stats
    safety_stats = {}
    safety = db.query(
        db.func.concat(
            db.case((DuengerModel.wassergefaehrdend == True, "WG"), else_=""),
            db.case((DuengerModel.gefahrstoff_klasse.isnot(None), "+GHS"), else_="")
        ),
        db.func.count(DuengerModel.id)
    ).filter(
        DuengerModel.tenant_id == effective_tenant,
        DuengerModel.ist_aktiv == True
    ).group_by(
        DuengerModel.wassergefaehrdend,
        DuengerModel.gefahrstoff_klasse
    ).all()

    for safety_type, count in safety:
        safety_stats[safety_type or "Standard"] = count

    # Stock stats
    stock_stats = db.query(
        db.func.sum(DuengerModel.lagerbestand),
        db.func.avg(DuengerModel.vk_preis)
    ).filter(
        DuengerModel.tenant_id == effective_tenant,
        DuengerModel.ist_aktiv == True
    ).first()

    return {
        "total_duenger": sum(type_stats.values()),
        "by_type": type_stats,
        "by_safety": safety_stats,
        "stock_summary": {
            "total_stock": float(stock_stats[0] or 0),
            "avg_price": float(stock_stats[1] or 0)
        }
    }