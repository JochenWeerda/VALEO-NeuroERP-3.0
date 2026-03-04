from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.domains.operations.models import KonContract, KonContractLine, KonContractMovement
from app.services.kontrakte_adapters import ArticleLookupAdapter, PartyLookupAdapter
from app.services.kontrakte_service import (
    KontraktAuditService,
    KontraktNumberRangeService,
    KontraktRestmengenService,
    KontraktSecurityService,
    KontraktValidationService,
)

router = APIRouter(prefix="/api/v1/kontrakte", tags=["kontrakte"])

ContractType = Literal["EINKAUF", "ZUKAUF", "VERKAUF"]
StatusType = Literal["OFFEN", "ERLEDIGT", "STORNIERT"]
QuantityType = Literal["GESAMTKONTRAKT", "EINZELMENGEN"]


class KonContractLineIn(BaseModel):
    line_id: Optional[str] = None
    position_no: int = Field(..., ge=1)
    article_id: str
    description1: Optional[str] = None
    description2: Optional[str] = None
    qty_contract: float = Field(..., ge=0)
    price_unit: Optional[str] = None
    unit_price: Optional[float] = None
    discount_pct: Optional[float] = None
    surcharge: Optional[float] = None
    rebate_type: Optional[str] = None
    is_bio: bool = False
    is_matif: bool = False


class KonContractIn(BaseModel):
    contract_no: Optional[str] = None
    contract_type: ContractType
    branch_id: Optional[str] = None
    clerk_id: Optional[str] = None
    party_id: str
    debitor_kto: Optional[str] = None
    kreditor_kto: Optional[str] = None
    contract_date: Optional[datetime] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    quantity_type: QuantityType = "GESAMTKONTRAKT"
    total_quantity: float = Field(default=0, ge=0)
    unit: str = "kg"
    allow_overdelivery: bool = False
    status: StatusType = "OFFEN"
    notes: Optional[str] = None
    payment_terms: Optional[str] = None
    conditions_json: Optional[dict[str, Any]] = None
    pricing_model: Optional[str] = None
    min_price: Optional[float] = None
    premium_type: Optional[str] = None
    premium_value: Optional[float] = None
    basis_reference: Optional[str] = None
    pricing_window_from: Optional[datetime] = None
    pricing_window_to: Optional[datetime] = None
    lines: list[KonContractLineIn] = Field(default_factory=list)


class KonContractMovementOut(BaseModel):
    movement_id: str
    contract_id: str
    line_id: Optional[str] = None
    order_no: Optional[str] = None
    delivery_note_no: Optional[str] = None
    invoice_no: Optional[str] = None
    movement_date: Optional[datetime] = None
    quantity: float
    unit_price: Optional[float] = None
    route_no: Optional[str] = None
    is_invoiced: bool
    is_archived: bool


class KonContractMovementIn(BaseModel):
    line_id: str
    order_no: Optional[str] = None
    delivery_note_no: Optional[str] = None
    invoice_no: Optional[str] = None
    movement_date: Optional[datetime] = None
    quantity: float = Field(..., gt=0)
    unit_price: Optional[float] = None
    route_no: Optional[str] = None
    is_invoiced: bool = False
    is_archived: bool = False


def _require_roles(user: User, *roles: str) -> None:
    if not KontraktSecurityService.has_any_role(user.get("roles") or [], *roles):
        raise HTTPException(status_code=403, detail=f"Insufficient role. Required any of {roles}")


def _line_to_out(line: KonContractLine, rest: Optional[Decimal] = None) -> dict[str, Any]:
    return {
        "line_id": line.line_id,
        "position_no": line.position_no,
        "article_id": line.article_id,
        "description1": line.description1,
        "description2": line.description2,
        "qty_contract": float(line.qty_contract or 0),
        "qty_remaining": float(rest) if rest is not None else None,
        "price_unit": line.price_unit,
        "unit_price": float(line.unit_price) if line.unit_price is not None else None,
        "discount_pct": float(line.discount_pct) if line.discount_pct is not None else None,
        "surcharge": float(line.surcharge) if line.surcharge is not None else None,
        "rebate_type": line.rebate_type,
        "is_bio": bool(line.is_bio),
        "is_matif": bool(line.is_matif),
    }


def _contract_to_out(contract: KonContract, line_out: list[dict[str, Any]], contract_rest: Decimal) -> dict[str, Any]:
    return {
        "contract_id": contract.contract_id,
        "contract_no": contract.contract_no,
        "contract_type": contract.contract_type,
        "branch_id": contract.branch_id,
        "clerk_id": contract.clerk_id,
        "party_id": contract.party_id,
        "debitor_kto": contract.debitor_kto,
        "kreditor_kto": contract.kreditor_kto,
        "contract_date": contract.contract_date,
        "valid_from": contract.valid_from,
        "valid_to": contract.valid_to,
        "quantity_type": contract.quantity_type,
        "total_quantity": float(contract.total_quantity or 0),
        "unit": contract.unit,
        "allow_overdelivery": bool(contract.allow_overdelivery),
        "status": contract.status,
        "notes": contract.notes,
        "payment_terms": contract.payment_terms,
        "conditions_json": contract.conditions_json or {},
        "pricing_model": contract.pricing_model,
        "min_price": float(contract.min_price) if contract.min_price is not None else None,
        "premium_type": contract.premium_type,
        "premium_value": float(contract.premium_value) if contract.premium_value is not None else None,
        "basis_reference": contract.basis_reference,
        "pricing_window_from": contract.pricing_window_from,
        "pricing_window_to": contract.pricing_window_to,
        "rest_quantity": float(contract_rest),
        "created_at": contract.created_at,
        "created_by": contract.created_by,
        "updated_at": contract.updated_at,
        "updated_by": contract.updated_by,
        "lines": line_out,
    }


@router.get("")
async def list_kontrakte(
    status: Optional[StatusType] = Query(None),
    contract_type: Optional[ContractType] = Query(None),
    party_id: Optional[str] = Query(None),
    article_id: Optional[str] = Query(None),
    valid_from: Optional[datetime] = Query(None),
    valid_to: Optional[datetime] = Query(None),
    query: Optional[str] = Query(None),
    include_done: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    _require_roles(
        user,
        KontraktSecurityService.ROLE_LESEN,
        KontraktSecurityService.ROLE_BEARBEITEN,
        KontraktSecurityService.ROLE_ADMIN,
    )
    q = db.query(KonContract).filter(KonContract.tenant_id == tenant_id)
    if status:
        q = q.filter(KonContract.status == status)
    if contract_type:
        q = q.filter(KonContract.contract_type == contract_type)
    if party_id:
        q = q.filter(KonContract.party_id == party_id)
    if valid_from:
        q = q.filter(KonContract.valid_to >= valid_from)
    if valid_to:
        q = q.filter(KonContract.valid_from <= valid_to)
    if not include_done:
        q = q.filter(KonContract.status != "ERLEDIGT")
    if query:
        like = f"%{query}%"
        q = q.filter((KonContract.contract_no.ilike(like)) | (KonContract.party_id.ilike(like)))
    if article_id:
        q = q.join(KonContractLine, KonContractLine.contract_id == KonContract.contract_id).filter(KonContractLine.article_id == article_id)
    total = q.count()
    items = q.order_by(KonContract.updated_at.desc(), KonContract.created_at.desc()).offset(skip).limit(limit).all()
    rest_service = KontraktRestmengenService(db)
    payload = []
    for c in items:
        rest = rest_service.compute_rest(tenant_id, c.contract_id)
        payload.append(
            {
                "contract_id": c.contract_id,
                "contract_no": c.contract_no,
                "contract_type": c.contract_type,
                "party_id": c.party_id,
                "contract_date": c.contract_date,
                "valid_from": c.valid_from,
                "valid_to": c.valid_to,
                "total_quantity": float(c.total_quantity or 0),
                "rest_quantity": float(rest.contract_rest),
                "unit": c.unit,
                "status": c.status,
                "pricing_model": c.pricing_model,
                "allow_overdelivery": bool(c.allow_overdelivery),
            }
        )
    return {"items": payload, "total": total, "skip": skip, "limit": limit}


@router.get("/{contract_id}")
async def get_kontrakt(
    contract_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    _require_roles(
        user,
        KontraktSecurityService.ROLE_LESEN,
        KontraktSecurityService.ROLE_BEARBEITEN,
        KontraktSecurityService.ROLE_ADMIN,
    )
    contract = db.query(KonContract).filter(KonContract.tenant_id == tenant_id, KonContract.contract_id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    rest_service = KontraktRestmengenService(db)
    rest = rest_service.compute_rest(tenant_id, contract_id)
    lines = db.query(KonContractLine).filter(KonContractLine.tenant_id == tenant_id, KonContractLine.contract_id == contract_id).order_by(KonContractLine.position_no.asc()).all()
    line_out = [_line_to_out(line, rest.line_rest.get(line.line_id)) for line in lines]
    return _contract_to_out(contract, line_out, rest.contract_rest)


@router.post("")
async def create_kontrakt(
    payload: KonContractIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    _require_roles(user, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
    KontraktValidationService.validate_contract_type(payload.contract_type)
    KontraktValidationService.validate_quantity_type(payload.quantity_type)
    KontraktValidationService.validate_status(payload.status)

    roles = user.get("roles") or []
    contract_no = payload.contract_no
    if contract_no:
        if not KontraktSecurityService.has_any_role(roles, KontraktSecurityService.ROLE_ADMIN):
            raise HTTPException(status_code=403, detail="Manual contract number requires KONTRAKT_ADMIN")
    else:
        contract_no = KontraktNumberRangeService(db).next_contract_no(tenant_id, payload.contract_type, payload.branch_id)

    if db.query(KonContract).filter(KonContract.tenant_id == tenant_id, KonContract.contract_no == contract_no).first():
        raise HTTPException(status_code=409, detail="contract_no already exists")

    contract = KonContract(
        contract_id=uuid7(),
        contract_no=contract_no,
        contract_type=payload.contract_type,
        branch_id=payload.branch_id,
        clerk_id=payload.clerk_id,
        party_id=payload.party_id,
        debitor_kto=payload.debitor_kto,
        kreditor_kto=payload.kreditor_kto,
        contract_date=payload.contract_date or datetime.utcnow(),
        valid_from=payload.valid_from,
        valid_to=payload.valid_to,
        quantity_type=payload.quantity_type,
        total_quantity=payload.total_quantity,
        unit=payload.unit,
        allow_overdelivery=payload.allow_overdelivery,
        status=payload.status,
        notes=payload.notes,
        payment_terms=payload.payment_terms,
        conditions_json=payload.conditions_json or {},
        pricing_model=payload.pricing_model,
        min_price=payload.min_price,
        premium_type=payload.premium_type,
        premium_value=payload.premium_value,
        basis_reference=payload.basis_reference,
        pricing_window_from=payload.pricing_window_from,
        pricing_window_to=payload.pricing_window_to,
        tenant_id=tenant_id,
        created_by=user.get("sub"),
        updated_by=user.get("sub"),
    )
    db.add(contract)
    db.flush()

    for line_in in payload.lines:
        db.add(
            KonContractLine(
                line_id=uuid7(),
                contract_id=contract.contract_id,
                position_no=line_in.position_no,
                article_id=line_in.article_id,
                description1=line_in.description1,
                description2=line_in.description2,
                qty_contract=line_in.qty_contract,
                price_unit=line_in.price_unit,
                unit_price=line_in.unit_price,
                discount_pct=line_in.discount_pct,
                surcharge=line_in.surcharge,
                rebate_type=line_in.rebate_type,
                is_bio=line_in.is_bio,
                is_matif=line_in.is_matif,
                tenant_id=tenant_id,
                created_by=user.get("sub"),
                updated_by=user.get("sub"),
            )
        )
    KontraktAuditService(db).log_change(
        tenant_id=tenant_id,
        entity_type="kon_contract",
        entity_id=contract.contract_id,
        field_name="contract_no",
        action="CREATE",
        changed_by=user.get("sub"),
        old_value=None,
        new_value=contract_no,
    )
    db.commit()
    return await get_kontrakt(contract.contract_id, db, tenant_id, user)


@router.patch("/{contract_id}")
async def update_kontrakt(
    contract_id: str,
    payload: KonContractIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    _require_roles(user, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
    contract = db.query(KonContract).filter(KonContract.tenant_id == tenant_id, KonContract.contract_id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    if payload.status in {"ERLEDIGT", "STORNIERT"} and not KontraktSecurityService.has_any_role(
        user.get("roles") or [], KontraktSecurityService.ROLE_ADMIN
    ):
        raise HTTPException(status_code=403, detail="Manual status override requires KONTRAKT_ADMIN")

    update_data = payload.model_dump(exclude_unset=True)
    if "lines" in update_data:
        update_data.pop("lines")

    audit = KontraktAuditService(db)
    audit.log_diff_for_contract(
        tenant_id=tenant_id,
        contract_id=contract_id,
        changed_by=user.get("sub"),
        before=contract,
        after_payload=update_data,
    )
    for k, v in update_data.items():
        if k == "contract_no" and v and v != contract.contract_no:
            if not KontraktSecurityService.has_any_role(user.get("roles") or [], KontraktSecurityService.ROLE_ADMIN):
                raise HTTPException(status_code=403, detail="Manual contract number change requires KONTRAKT_ADMIN")
        setattr(contract, k, v)
    contract.updated_by = user.get("sub")

    if payload.lines:
        db.query(KonContractLine).filter(KonContractLine.tenant_id == tenant_id, KonContractLine.contract_id == contract_id).delete()
        for line_in in payload.lines:
            db.add(
                KonContractLine(
                    line_id=line_in.line_id or uuid7(),
                    contract_id=contract_id,
                    position_no=line_in.position_no,
                    article_id=line_in.article_id,
                    description1=line_in.description1,
                    description2=line_in.description2,
                    qty_contract=line_in.qty_contract,
                    price_unit=line_in.price_unit,
                    unit_price=line_in.unit_price,
                    discount_pct=line_in.discount_pct,
                    surcharge=line_in.surcharge,
                    rebate_type=line_in.rebate_type,
                    is_bio=line_in.is_bio,
                    is_matif=line_in.is_matif,
                    tenant_id=tenant_id,
                    updated_by=user.get("sub"),
                    created_by=user.get("sub"),
                )
            )
    db.commit()
    return await get_kontrakt(contract_id, db, tenant_id, user)


@router.delete("/{contract_id}")
async def delete_kontrakt(
    contract_id: str,
    force: bool = Query(False),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    contract = db.query(KonContract).filter(KonContract.tenant_id == tenant_id, KonContract.contract_id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    has_movements = (
        db.query(KonContractMovement)
        .filter(KonContractMovement.tenant_id == tenant_id, KonContractMovement.contract_id == contract_id)
        .first()
        is not None
    )
    roles = user.get("roles") or []
    if has_movements:
        if not KontraktSecurityService.has_any_role(roles, KontraktSecurityService.ROLE_ADMIN):
            raise HTTPException(status_code=403, detail="Deleting contracts with movements requires KONTRAKT_ADMIN")
        if not force:
            raise HTTPException(status_code=400, detail="force=true required when movements exist")
    else:
        _require_roles(user, KontraktSecurityService.ROLE_LOESCHEN, KontraktSecurityService.ROLE_ADMIN)
    db.delete(contract)
    KontraktAuditService(db).log_change(
        tenant_id=tenant_id,
        entity_type="kon_contract",
        entity_id=contract_id,
        field_name="contract_id",
        action="DELETE",
        changed_by=user.get("sub"),
        old_value=contract_id,
        new_value=None,
    )
    db.commit()
    return {"ok": True}


@router.post("/{contract_id}/cancel")
async def cancel_kontrakt(
    contract_id: str,
    reason: Optional[str] = Body(default=None, embed=True),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    _require_roles(user, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
    contract = db.query(KonContract).filter(KonContract.tenant_id == tenant_id, KonContract.contract_id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    old_status = contract.status
    contract.status = "STORNIERT"
    contract.updated_by = user.get("sub")
    KontraktAuditService(db).log_change(
        tenant_id=tenant_id,
        entity_type="kon_contract",
        entity_id=contract_id,
        field_name="status",
        action="CANCEL",
        changed_by=user.get("sub"),
        old_value=old_status,
        new_value="STORNIERT",
    )
    if reason:
        KontraktAuditService(db).log_change(
            tenant_id=tenant_id,
            entity_type="kon_contract",
            entity_id=contract_id,
            field_name="cancel_reason",
            action="CANCEL",
            changed_by=user.get("sub"),
            old_value=None,
            new_value=reason,
        )
    db.commit()
    return await get_kontrakt(contract_id, db, tenant_id, user)


@router.get("/{contract_id}/movements")
async def list_kontrakt_movements(
    contract_id: str,
    include_archived: bool = Query(False),
    only_invoiced: Optional[bool] = Query(None),
    article_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    _require_roles(
        user,
        KontraktSecurityService.ROLE_LESEN,
        KontraktSecurityService.ROLE_BEARBEITEN,
        KontraktSecurityService.ROLE_ADMIN,
    )
    rows = (
        db.query(KonContractMovement)
        .filter(KonContractMovement.tenant_id == tenant_id, KonContractMovement.contract_id == contract_id)
        .order_by(KonContractMovement.movement_date.desc())
    )
    if not include_archived:
        rows = rows.filter(KonContractMovement.is_archived.is_(False))
    if only_invoiced is not None:
        rows = rows.filter(KonContractMovement.is_invoiced.is_(only_invoiced))
    if article_id:
        line_ids = [r[0] for r in db.query(KonContractLine.line_id).filter(
            KonContractLine.tenant_id == tenant_id,
            KonContractLine.contract_id == contract_id,
            KonContractLine.article_id == article_id,
        ).all()]
        if line_ids:
            rows = rows.filter(KonContractMovement.line_id.in_(line_ids))
        else:
            rows = rows.filter(False)
    payload = [
        KonContractMovementOut(
            movement_id=r.movement_id,
            contract_id=r.contract_id,
            line_id=r.line_id,
            order_no=r.order_no,
            delivery_note_no=r.delivery_note_no,
            invoice_no=r.invoice_no,
            movement_date=r.movement_date,
            quantity=float(r.quantity or 0),
            unit_price=float(r.unit_price) if r.unit_price is not None else None,
            route_no=r.route_no,
            is_invoiced=bool(r.is_invoiced),
            is_archived=bool(r.is_archived),
        ).model_dump()
        for r in rows.all()
    ]
    verk_menge = sum(Decimal(str(r["quantity"])) for r in payload)
    return {"items": payload, "verk_menge": float(verk_menge)}


@router.post("/{contract_id}/movements")
async def create_kontrakt_movement(
    contract_id: str,
    payload: KonContractMovementIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    _require_roles(user, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
    contract = db.query(KonContract).filter(KonContract.tenant_id == tenant_id, KonContract.contract_id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    line = (
        db.query(KonContractLine)
        .filter(
            KonContractLine.tenant_id == tenant_id,
            KonContractLine.contract_id == contract_id,
            KonContractLine.line_id == payload.line_id,
        )
        .first()
    )
    if not line:
        raise HTTPException(status_code=404, detail="Contract line not found")

    rest_service = KontraktRestmengenService(db)
    rest = rest_service.compute_rest(tenant_id, contract_id)
    line_rest = rest.line_rest.get(payload.line_id, Decimal("0"))
    try:
        rest_service.enforce_overdelivery(
            bool(contract.allow_overdelivery),
            line_rest,
            Decimal(str(payload.quantity)),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    movement = KonContractMovement(
        movement_id=uuid7(),
        contract_id=contract_id,
        line_id=payload.line_id,
        order_no=payload.order_no,
        delivery_note_no=payload.delivery_note_no,
        invoice_no=payload.invoice_no,
        movement_date=payload.movement_date or datetime.utcnow(),
        quantity=payload.quantity,
        unit_price=payload.unit_price,
        route_no=payload.route_no,
        is_invoiced=payload.is_invoiced,
        is_archived=payload.is_archived,
        tenant_id=tenant_id,
        created_by=user.get("sub"),
    )
    db.add(movement)
    db.flush()

    rest_after = rest_service.compute_rest(tenant_id, contract_id)
    contract.status = KontraktRestmengenService.determine_status_from_rest(
        bool(contract.allow_overdelivery),
        contract.status or "OFFEN",
        rest_after.contract_rest,
    )
    contract.updated_by = user.get("sub")
    KontraktAuditService(db).log_change(
        tenant_id=tenant_id,
        entity_type="kon_contract_movement",
        entity_id=contract_id,
        field_name="quantity",
        action="CREATE",
        changed_by=user.get("sub"),
        old_value=None,
        new_value=payload.quantity,
    )
    db.commit()
    db.refresh(movement)
    return KonContractMovementOut(
        movement_id=movement.movement_id,
        contract_id=movement.contract_id,
        line_id=movement.line_id,
        order_no=movement.order_no,
        delivery_note_no=movement.delivery_note_no,
        invoice_no=movement.invoice_no,
        movement_date=movement.movement_date,
        quantity=float(movement.quantity or 0),
        unit_price=float(movement.unit_price) if movement.unit_price is not None else None,
        route_no=movement.route_no,
        is_invoiced=bool(movement.is_invoiced),
        is_archived=bool(movement.is_archived),
    ).model_dump()


@router.get("/{contract_id}/audit")
async def list_kontrakt_audit(
    contract_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    _require_roles(
        user,
        KontraktSecurityService.ROLE_LESEN,
        KontraktSecurityService.ROLE_BEARBEITEN,
        KontraktSecurityService.ROLE_ADMIN,
    )
    rows = (
        db.query(func.count())
        .select_from(KonContract)
        .filter(KonContract.tenant_id == tenant_id, KonContract.contract_id == contract_id)
        .scalar()
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Contract not found")
    from app.domains.operations.models import KonAuditLog

    logs = (
        db.query(KonAuditLog)
        .filter(KonAuditLog.tenant_id == tenant_id, KonAuditLog.entity_id == contract_id)
        .order_by(KonAuditLog.changed_at.desc())
        .all()
    )
    return {
        "items": [
            {
                "audit_id": l.audit_id,
                "entity_type": l.entity_type,
                "entity_id": l.entity_id,
                "field_name": l.field_name,
                "old_value": l.old_value,
                "new_value": l.new_value,
                "action": l.action,
                "changed_at": l.changed_at,
                "changed_by": l.changed_by,
            }
            for l in logs
        ]
    }


@router.post("/lookup/verkauf")
async def lookup_verkauf_kontrakte(
    query: Optional[str] = Body(default=None),
    only_open: bool = Body(default=True),
    limit: int = Body(default=50),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    _require_roles(
        user,
        KontraktSecurityService.ROLE_LESEN,
        KontraktSecurityService.ROLE_BEARBEITEN,
        KontraktSecurityService.ROLE_ADMIN,
    )
    q = db.query(KonContract).filter(KonContract.tenant_id == tenant_id, KonContract.contract_type == "VERKAUF")
    if only_open:
        q = q.filter(KonContract.status != "ERLEDIGT", KonContract.status != "STORNIERT")
    if query:
        like = f"%{query.strip()}%"
        q = q.filter((KonContract.contract_no.ilike(like)) | (KonContract.party_id.ilike(like)))
    contracts = q.order_by(KonContract.updated_at.desc()).limit(max(1, min(limit, 200))).all()
    party_lookup = PartyLookupAdapter(db)
    article_lookup = ArticleLookupAdapter(db)

    result: list[dict[str, Any]] = []
    for c in contracts:
        partner_name = party_lookup.get_name(c.party_id)
        lines = (
            db.query(KonContractLine)
            .filter(KonContractLine.tenant_id == tenant_id, KonContractLine.contract_id == c.contract_id)
            .order_by(KonContractLine.position_no.asc())
            .all()
        )
        for line in lines:
            article_name = article_lookup.get_label(line.article_id, line.description1)
            result.append(
                {
                    "contract_id": c.contract_id,
                    "line_id": line.line_id,
                    "contract_no": c.contract_no,
                    "position_no": line.position_no,
                    "date": c.contract_date,
                    "name": partner_name,
                    "valid_from": c.valid_from,
                    "valid_to": c.valid_to,
                    "article_id": line.article_id,
                    "bezeichnung": article_name,
                }
            )
    return {"items": result}
