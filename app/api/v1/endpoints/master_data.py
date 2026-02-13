"""
Master-data / Stammdaten endpoints (l3c-stammdaten)
Generic lookup tables: branches, countries, shipping methods, dispatchers, etc.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....infrastructure.models import MasterDataEntry, Dispatcher
from ..schemas.base import PaginatedResponse, BaseSchema

router = APIRouter()
DEFAULT_TENANT = "system"


# ── Schemas ──────────────────────────────────────────────────────

class MasterDataOut(BaseSchema):
    id: str
    category: str
    code: str
    label: str
    sort_order: int = 0


class MasterDataCreate(BaseModel):
    category: str
    code: str
    label: str
    sort_order: int = 0


class DispatcherOut(BaseSchema):
    id: str
    name: str
    code: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True


class DispatcherCreate(BaseModel):
    name: str
    code: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


# ── Generic master-data ─────────────────────────────────────────

@router.get("/", response_model=PaginatedResponse[MasterDataOut])
async def list_master_data(
    category: Optional[str] = Query(None, description="Filter by category"),
    tenant_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """GET Stammdaten (Branchen, Bundesländer, Staaten, Versandarten, etc.)"""
    tid = tenant_id or DEFAULT_TENANT
    q = db.query(MasterDataEntry).filter(
        MasterDataEntry.tenant_id == tid,
        MasterDataEntry.is_active == True,  # noqa: E712
    )
    if category:
        q = q.filter(MasterDataEntry.category == category)
    q = q.order_by(MasterDataEntry.sort_order, MasterDataEntry.label)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    page = (skip // limit) + 1
    pages = max((total + limit - 1) // limit, 1)
    return PaginatedResponse[MasterDataOut](
        items=[MasterDataOut.model_validate(i) for i in items],
        total=total, page=page, size=limit, pages=pages,
        has_next=(skip + limit) < total, has_prev=skip > 0,
    )


@router.post("/", response_model=MasterDataOut, status_code=201)
async def create_master_data(
    payload: MasterDataCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """POST Stammdaten anlegen"""
    import uuid
    tid = tenant_id or DEFAULT_TENANT
    obj = MasterDataEntry(
        id=str(uuid.uuid4()),
        category=payload.category,
        code=payload.code,
        label=payload.label,
        sort_order=payload.sort_order,
        tenant_id=tid,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return MasterDataOut.model_validate(obj)


# ── Convenience category endpoints ──────────────────────────────

@router.get("/branches", response_model=list[MasterDataOut])
async def list_branches(tenant_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """GET Branchen"""
    tid = tenant_id or DEFAULT_TENANT
    items = db.query(MasterDataEntry).filter(
        MasterDataEntry.tenant_id == tid,
        MasterDataEntry.category == "branch",
        MasterDataEntry.is_active == True,  # noqa: E712
    ).order_by(MasterDataEntry.sort_order).all()
    return [MasterDataOut.model_validate(i) for i in items]


@router.get("/countries", response_model=list[MasterDataOut])
async def list_countries(tenant_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """GET Staaten ermitteln"""
    tid = tenant_id or DEFAULT_TENANT
    items = db.query(MasterDataEntry).filter(
        MasterDataEntry.tenant_id == tid,
        MasterDataEntry.category == "country",
        MasterDataEntry.is_active == True,  # noqa: E712
    ).order_by(MasterDataEntry.label).all()
    return [MasterDataOut.model_validate(i) for i in items]


@router.get("/shipping-methods", response_model=list[MasterDataOut])
async def list_shipping_methods(tenant_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """GET Versandarten"""
    tid = tenant_id or DEFAULT_TENANT
    items = db.query(MasterDataEntry).filter(
        MasterDataEntry.tenant_id == tid,
        MasterDataEntry.category == "shipping_method",
        MasterDataEntry.is_active == True,  # noqa: E712
    ).order_by(MasterDataEntry.sort_order).all()
    return [MasterDataOut.model_validate(i) for i in items]


@router.get("/units", response_model=list[MasterDataOut])
async def list_units_of_measure(tenant_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """GET MengenEinheiten"""
    tid = tenant_id or DEFAULT_TENANT
    items = db.query(MasterDataEntry).filter(
        MasterDataEntry.tenant_id == tid,
        MasterDataEntry.category == "unit",
        MasterDataEntry.is_active == True,  # noqa: E712
    ).order_by(MasterDataEntry.sort_order).all()
    return [MasterDataOut.model_validate(i) for i in items]


@router.get("/container-units", response_model=list[MasterDataOut])
async def list_container_units(tenant_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """GET GebindeEinheiten"""
    tid = tenant_id or DEFAULT_TENANT
    items = db.query(MasterDataEntry).filter(
        MasterDataEntry.tenant_id == tid,
        MasterDataEntry.category == "container_unit",
        MasterDataEntry.is_active == True,  # noqa: E712
    ).order_by(MasterDataEntry.sort_order).all()
    return [MasterDataOut.model_validate(i) for i in items]


@router.get("/contact-types", response_model=list[MasterDataOut])
async def list_contact_types(tenant_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """GET Kontaktarten ermitteln"""
    tid = tenant_id or DEFAULT_TENANT
    items = db.query(MasterDataEntry).filter(
        MasterDataEntry.tenant_id == tid,
        MasterDataEntry.category == "contact_type",
        MasterDataEntry.is_active == True,  # noqa: E712
    ).order_by(MasterDataEntry.sort_order).all()
    return [MasterDataOut.model_validate(i) for i in items]


@router.post("/contact-types", response_model=MasterDataOut, status_code=201)
async def create_contact_type(
    payload: MasterDataCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """POST Kontaktart Anlegen"""
    import uuid
    tid = tenant_id or DEFAULT_TENANT
    obj = MasterDataEntry(
        id=str(uuid.uuid4()),
        category="contact_type",
        code=payload.code,
        label=payload.label,
        sort_order=payload.sort_order,
        tenant_id=tid,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return MasterDataOut.model_validate(obj)


@router.delete("/contact-types/{ct_id}", status_code=204)
async def delete_contact_type(ct_id: str, db: Session = Depends(get_db)):
    """DEL Kontaktart Löschen"""
    obj = db.query(MasterDataEntry).filter(MasterDataEntry.id == ct_id).first()
    if not obj:
        raise HTTPException(404, "Contact type not found")
    db.delete(obj)
    db.commit()


# ── Dispatchers ──────────────────────────────────────────────────

@router.get("/dispatchers", response_model=list[DispatcherOut])
async def list_dispatchers(tenant_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """GET Disponent ermitteln"""
    tid = tenant_id or DEFAULT_TENANT
    items = db.query(Dispatcher).filter(
        Dispatcher.tenant_id == tid,
        Dispatcher.is_active == True,  # noqa: E712
    ).all()
    return [DispatcherOut.model_validate(i) for i in items]


@router.post("/dispatchers", response_model=DispatcherOut, status_code=201)
async def create_dispatcher(
    payload: DispatcherCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """POST Disponent anlegen"""
    import uuid
    tid = tenant_id or DEFAULT_TENANT
    obj = Dispatcher(
        id=str(uuid.uuid4()),
        name=payload.name,
        code=payload.code,
        email=payload.email,
        phone=payload.phone,
        tenant_id=tid,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return DispatcherOut.model_validate(obj)


@router.put("/dispatchers/{disp_id}", response_model=DispatcherOut)
async def update_dispatcher(
    disp_id: str, payload: DispatcherCreate, db: Session = Depends(get_db),
):
    """PUT Disponent bearbeiten"""
    obj = db.query(Dispatcher).filter(Dispatcher.id == disp_id).first()
    if not obj:
        raise HTTPException(404, "Dispatcher not found")
    for f, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, f, v)
    db.commit()
    db.refresh(obj)
    return DispatcherOut.model_validate(obj)


@router.delete("/dispatchers/{disp_id}", status_code=204)
async def delete_dispatcher(disp_id: str, db: Session = Depends(get_db)):
    """DEL Disponent löschen"""
    obj = db.query(Dispatcher).filter(Dispatcher.id == disp_id).first()
    if not obj:
        raise HTTPException(404, "Dispatcher not found")
    db.delete(obj)
    db.commit()
