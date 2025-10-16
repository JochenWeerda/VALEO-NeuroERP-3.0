"""
Saatgut API endpoints
Full CRUD for Saatgut-Stammdaten management
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from ....core.database import get_db
from ....infrastructure.models import Saatgut as SaatgutModel
from ....api.v1.schemas.base import PaginatedResponse
from ....api.v1.schemas.agrar import Saatgut, SaatgutCreate, SaatgutUpdate

router = APIRouter()

DEFAULT_TENANT = "system"


@router.get("/", response_model=PaginatedResponse[Saatgut])
async def list_saatgut(
    tenant_id: Optional[str] = Query(None, description="Filter by tenant ID"),
    search: Optional[str] = Query(None, description="Search in name, article number, variety"),
    art: Optional[str] = Query(None, description="Filter by type (Weizen, Gerste, etc.)"),
    zuechter: Optional[str] = Query(None, description="Filter by breeder"),
    bsa_zulassung: Optional[bool] = Query(None, description="Filter by BSA approval"),
    eu_zulassung: Optional[bool] = Query(None, description="Filter by EU approval"),
    ist_aktiv: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(25, ge=1, le=200, description="Maximum number of records"),
    db: Session = Depends(get_db),
):
    """Return a paginated list of Saatgut."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    query = db.query(SaatgutModel).filter(SaatgutModel.tenant_id == effective_tenant)

    if ist_aktiv is not None:
        query = query.filter(SaatgutModel.ist_aktiv == ist_aktiv)

    if art:
        query = query.filter(SaatgutModel.art == art)

    if zuechter:
        query = query.filter(SaatgutModel.zuechter == zuechter)

    if bsa_zulassung is not None:
        query = query.filter(SaatgutModel.bsa_zulassung == bsa_zulassung)

    if eu_zulassung is not None:
        query = query.filter(SaatgutModel.eu_zulassung == eu_zulassung)

    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                SaatgutModel.name.ilike(like),
                SaatgutModel.artikelnummer.ilike(like),
                SaatgutModel.sorte.ilike(like),
                SaatgutModel.zuechter.ilike(like),
            )
        )

    total = query.count()
    items = query.order_by(desc(SaatgutModel.created_at)).offset(skip).limit(limit).all()

    page = (skip // limit) + 1
    pages = (total + limit - 1) // limit if total else 1

    return PaginatedResponse(
        items=[Saatgut.model_validate(item) for item in items],
        total=total,
        page=page,
        pages=pages,
        size=limit,
        has_next=(skip + limit) < total,
        has_prev=skip > 0,
    )


@router.get("/{saatgut_id}", response_model=Saatgut)
async def get_saatgut(
    saatgut_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get a single Saatgut by ID."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    saatgut = (
        db.query(SaatgutModel)
        .filter(
            SaatgutModel.id == saatgut_id,
            SaatgutModel.tenant_id == effective_tenant
        )
        .first()
    )

    if not saatgut:
        raise HTTPException(status_code=404, detail="Saatgut not found")

    return Saatgut.model_validate(saatgut)


@router.post("/", response_model=Saatgut, status_code=201)
async def create_saatgut(
    saatgut_data: SaatgutCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Create a new Saatgut."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    # Check if artikelnummer already exists
    existing = (
        db.query(SaatgutModel)
        .filter(
            SaatgutModel.artikelnummer == saatgut_data.artikelnummer,
            SaatgutModel.tenant_id == effective_tenant
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Saatgut with article number {saatgut_data.artikelnummer} already exists"
        )

    # Validate business rules
    if saatgut_data.ablauf_zulassung and saatgut_data.ablauf_zulassung < datetime.utcnow().date():
        raise HTTPException(
            status_code=400,
            detail="Approval expiry date cannot be in the past"
        )

    saatgut = SaatgutModel(
        **saatgut_data.model_dump(),
        tenant_id=effective_tenant
    )

    db.add(saatgut)
    db.commit()
    db.refresh(saatgut)

    return Saatgut.model_validate(saatgut)


@router.put("/{saatgut_id}", response_model=Saatgut)
async def update_saatgut(
    saatgut_id: str,
    saatgut_data: SaatgutUpdate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Update an existing Saatgut."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    saatgut = (
        db.query(SaatgutModel)
        .filter(
            SaatgutModel.id == saatgut_id,
            SaatgutModel.tenant_id == effective_tenant
        )
        .first()
    )

    if not saatgut:
        raise HTTPException(status_code=404, detail="Saatgut not found")

    update_data = saatgut_data.model_dump(exclude_unset=True)

    # Validate artikelnummer uniqueness if changed
    if "artikelnummer" in update_data and update_data["artikelnummer"] != saatgut.artikelnummer:
        existing = (
            db.query(SaatgutModel)
            .filter(
                SaatgutModel.artikelnummer == update_data["artikelnummer"],
                SaatgutModel.tenant_id == effective_tenant,
                SaatgutModel.id != saatgut_id
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Saatgut with article number {update_data['artikelnummer']} already exists"
            )

    # Validate approval expiry
    if "ablauf_zulassung" in update_data and update_data["ablauf_zulassung"]:
        from datetime import datetime
        if update_data["ablauf_zulassung"] < datetime.utcnow().date():
            raise HTTPException(
                status_code=400,
                detail="Approval expiry date cannot be in the past"
            )

    for key, value in update_data.items():
        setattr(saatgut, key, value)

    db.commit()
    db.refresh(saatgut)

    return Saatgut.model_validate(saatgut)


@router.delete("/{saatgut_id}", status_code=204)
async def delete_saatgut(
    saatgut_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Delete a Saatgut (soft delete)."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    saatgut = (
        db.query(SaatgutModel)
        .filter(
            SaatgutModel.id == saatgut_id,
            SaatgutModel.tenant_id == effective_tenant
        )
        .first()
    )

    if not saatgut:
        raise HTTPException(status_code=404, detail="Saatgut not found")

    saatgut.ist_aktiv = False
    db.commit()

    return None


@router.get("/search", response_model=list[Saatgut])
async def search_saatgut(
    q: str = Query(..., min_length=2, description="Search term"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Lightweight search endpoint for Saatgut."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    like = f"%{q}%"

    query = (
        db.query(SaatgutModel)
        .filter(SaatgutModel.ist_aktiv == True)
        .filter(SaatgutModel.tenant_id == effective_tenant)
        .filter(
            or_(
                SaatgutModel.name.ilike(like),
                SaatgutModel.artikelnummer.ilike(like),
                SaatgutModel.sorte.ilike(like),
            )
        )
        .order_by(SaatgutModel.name.asc())
        .limit(limit)
    )

    return [Saatgut.model_validate(item) for item in query.all()]


@router.get("/stats/overview")
async def get_saatgut_stats(
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get Saatgut statistics overview."""
    effective_tenant = tenant_id or DEFAULT_TENANT

    # Count by type
    type_stats = {}
    types = db.query(SaatgutModel.art, db.func.count(SaatgutModel.id)).filter(
        SaatgutModel.tenant_id == effective_tenant,
        SaatgutModel.ist_aktiv == True
    ).group_by(SaatgutModel.art).all()

    for art, count in types:
        type_stats[art or "Unbekannt"] = count

    # Approval stats
    approval_stats = {}
    approvals = db.query(
        db.func.concat(
            db.case((SaatgutModel.bsa_zulassung == True, "BSA"), else_=""),
            db.case((SaatgutModel.eu_zulassung == True, "+EU"), else_="")
        ),
        db.func.count(SaatgutModel.id)
    ).filter(
        SaatgutModel.tenant_id == effective_tenant,
        SaatgutModel.ist_aktiv == True
    ).group_by(
        SaatgutModel.bsa_zulassung,
        SaatgutModel.eu_zulassung
    ).all()

    for approval_type, count in approvals:
        approval_stats[approval_type or "Keine Zulassung"] = count

    # Stock stats
    stock_stats = db.query(
        db.func.sum(SaatgutModel.lagerbestand),
        db.func.sum(SaatgutModel.verfuegbar),
        db.func.avg(SaatgutModel.vk_preis)
    ).filter(
        SaatgutModel.tenant_id == effective_tenant,
        SaatgutModel.ist_aktiv == True
    ).first()

    return {
        "total_saatgut": sum(type_stats.values()),
        "by_type": type_stats,
        "by_approval": approval_stats,
        "stock_summary": {
            "total_stock": float(stock_stats[0] or 0),
            "available_stock": float(stock_stats[1] or 0),
            "avg_price": float(stock_stats[2] or 0)
        }
    }