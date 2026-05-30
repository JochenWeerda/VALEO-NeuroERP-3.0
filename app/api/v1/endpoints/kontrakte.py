"""Kontrakte endpoints — contract CRUD, movements, amendments, dispositionen."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.domains.operations.models import KonContract, KonContractLine, KonContractMovement
from app.infrastructure.models.l3c_models import ContractAmendment, AmendmentTemplate
from app.services.kontrakte_adapters import ArticleLookupAdapter, PartyLookupAdapter
from app.services.kontrakte_service import (
    KontraktAuditService,
    KontraktNumberRangeService,
    KontraktRestmengenService,
    KontraktSecurityService,
    KontraktValidationService,
    build_contract_steering,
    contract_to_dict,
    create_disposition_db,
    ensure_disposition_table,
    line_to_dict,
    list_dispositionen_db,
    # Re-exports for backwards-compatibility with tests
    _bool,
    _date,
    _iso,
    _num,
    _string_list,
    _text,
    _contract_reference_price,
)

# Backwards-compatible alias for tests
_line_to_out = line_to_dict
from app.services.position_guard_service import PositionGuardService

from app.api.v1.schemas.kontrakte_schemas import (
    AmendmentCreate,
    AmendmentResponse,
    AmendmentStatusUpdate,
    AmendmentTemplateResponse,
    DispositionCreate,
    KonContractIn,
    KonContractMovementIn,
    KonContractMovementOut,
    KontraktOut,
)

router = APIRouter(prefix="/kontrakte", tags=["kontrakte"])


def _require_roles(user: User, *roles: str) -> None:
    if not KontraktSecurityService.has_any_role(user.get("roles") or [], *roles):
        raise HTTPException(status_code=403, detail=f"Insufficient role. Required any of {roles}")


# ── List ──────────────────────────────────────────────────────────────────────

@router.get("", response_model=KontraktOut, summary="Kontrakte auflisten")
async def list_kontrakte(
    status: Optional[str] = Query(None),
    contract_type: Optional[str] = Query(None),
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
    _require_roles(user, KontraktSecurityService.ROLE_LESEN, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
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
    q = q.filter(KonContract.status != "GELOESCHT")
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
    party_adapter = PartyLookupAdapter(db)
    payload = []
    for c in items:
        rest = rest_service.compute_rest(tenant_id, c.contract_id)
        first_line = db.query(KonContractLine).filter(
            KonContractLine.contract_id == c.contract_id, KonContractLine.tenant_id == tenant_id
        ).order_by(KonContractLine.position_no.asc()).first()
        party_name = party_adapter.get_name(c.party_id)
        first_unit_price = float(first_line.unit_price) if first_line and first_line.unit_price is not None else None
        steering = build_contract_steering(c, rest.contract_rest, first_unit_price)
        payload.append({
            "contract_id": c.contract_id,
            "contract_no": c.contract_no,
            "contract_type": c.contract_type,
            "party_id": c.party_id,
            "party_name": party_name,
            "contract_date": c.contract_date,
            "valid_from": c.valid_from,
            "valid_to": c.valid_to,
            "total_quantity": float(c.total_quantity or 0),
            "rest_quantity": float(rest.contract_rest),
            "unit": c.unit,
            "status": c.status,
            "pricing_model": c.pricing_model,
            "allow_overdelivery": bool(c.allow_overdelivery),
            "first_article_id": first_line.article_id if first_line else None,
            "first_article_desc": first_line.description1 if first_line else None,
            "first_unit_price": first_unit_price,
            "steering": steering,
        })
    return {"items": payload, "total": total, "skip": skip, "limit": limit}


# ── Detail ────────────────────────────────────────────────────────────────────

@router.get("/{contract_id}", response_model=KontraktOut, summary="Kontrakt abrufen")
async def get_kontrakt(
    contract_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    _require_roles(user, KontraktSecurityService.ROLE_LESEN, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
    contract = db.query(KonContract).filter(KonContract.tenant_id == tenant_id, KonContract.contract_id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    rest = KontraktRestmengenService(db).compute_rest(tenant_id, contract_id)
    lines = db.query(KonContractLine).filter(
        KonContractLine.tenant_id == tenant_id, KonContractLine.contract_id == contract_id
    ).order_by(KonContractLine.position_no.asc()).all()
    line_out = [line_to_dict(line, rest.line_rest.get(line.line_id)) for line in lines]
    return contract_to_dict(contract, line_out, rest.contract_rest)


# ── Create ────────────────────────────────────────────────────────────────────

def _position_guard_check(db: Session, tenant_id: str, payload: KonContractIn, user: User) -> None:
    """Check PositionGuard for VERKAUF contracts. Raises HTTPException on violation."""
    period_dt = payload.valid_to or payload.valid_from
    if not period_dt:
        return
    period_key = period_dt.strftime("%Y-%m") if hasattr(period_dt, "strftime") else None
    if not period_key:
        return
    guard = PositionGuardService(db)
    by_article: dict[str, Decimal] = defaultdict(Decimal)
    for line_in in payload.lines:
        by_article[line_in.article_id] += Decimal(str(line_in.qty_contract))
    for aid, delta in by_article.items():
        result = guard.check_impact(
            tenant_id=tenant_id,
            branch_id=payload.branch_id,
            article_id=aid,
            period_key=period_key,
            delta_sell_qty=delta,
            user_roles=user.get("roles") or [],
        )
        if not result.allowed:
            raise HTTPException(
                status_code=409,
                detail={
                    "guard": "short_violation",
                    "article_id": result.article_id,
                    "period_key": result.period_key,
                    "net_after": float(result.net_after) if result.net_after is not None else None,
                    "tolerance": float(result.tolerance) if result.tolerance is not None else None,
                    "message": result.reason,
                },
            )


def _add_lines(db: Session, contract_id: str, tenant_id: str, user: User, lines: list) -> None:
    for line_in in lines:
        db.add(KonContractLine(
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
            created_by=user.get("sub"),
            updated_by=user.get("sub"),
        ))


@router.post("", response_model=KontraktOut, summary="Kontrakt anlegen")
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

    if payload.contract_type == "VERKAUF" and payload.lines:
        _position_guard_check(db, tenant_id, payload, user)

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
    _add_lines(db, contract.contract_id, tenant_id, user, payload.lines)
    KontraktAuditService(db).log_change(
        tenant_id=tenant_id, entity_type="kon_contract", entity_id=contract.contract_id,
        field_name="contract_no", action="CREATE", changed_by=user.get("sub"),
        old_value=None, new_value=contract_no,
    )
    db.commit()
    return await get_kontrakt(contract.contract_id, db, tenant_id, user)


# ── Update / Replace ──────────────────────────────────────────────────────────

@router.patch("/{contract_id}", response_model=KontraktOut, summary="Kontrakt aktualisieren")
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
    update_data.pop("lines", None)

    audit = KontraktAuditService(db)
    audit.log_diff_for_contract(tenant_id=tenant_id, contract_id=contract_id, changed_by=user.get("sub"), before=contract, after_payload=update_data)
    for k, v in update_data.items():
        if k == "contract_no" and v and v != contract.contract_no:
            if not KontraktSecurityService.has_any_role(user.get("roles") or [], KontraktSecurityService.ROLE_ADMIN):
                raise HTTPException(status_code=403, detail="Manual contract number change requires KONTRAKT_ADMIN")
        setattr(contract, k, v)
    contract.updated_by = user.get("sub")

    if payload.lines and contract.contract_type == "VERKAUF":
        _position_guard_check(db, tenant_id, payload, user)

    if payload.lines:
        db.query(KonContractLine).filter(KonContractLine.tenant_id == tenant_id, KonContractLine.contract_id == contract_id).delete()
        _add_lines(db, contract_id, tenant_id, user, payload.lines)

    db.commit()
    return await get_kontrakt(contract_id, db, tenant_id, user)


@router.put("/{contract_id}", response_model=KontraktOut, summary="Kontrakt replace")
async def replace_kontrakt(
    contract_id: str,
    payload: KonContractIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    """Full replacement — delegates to PATCH logic."""
    return await update_kontrakt(contract_id, payload, db, tenant_id, user)


# ── Delete / Cancel ───────────────────────────────────────────────────────────

@router.delete("/{contract_id}", response_model=KontraktOut, summary="Kontrakt löschen")
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
    has_movements = db.query(KonContractMovement).filter(
        KonContractMovement.tenant_id == tenant_id, KonContractMovement.contract_id == contract_id
    ).first() is not None
    roles = user.get("roles") or []
    if has_movements:
        if not KontraktSecurityService.has_any_role(roles, KontraktSecurityService.ROLE_ADMIN):
            raise HTTPException(status_code=403, detail="Deleting contracts with movements requires KONTRAKT_ADMIN")
        if not force:
            raise HTTPException(status_code=409, detail="Kontrakt hat Umsaetze/Movements. Loeschung nur mit force=true (KONTRAKT_ADMIN).")
    else:
        _require_roles(user, KontraktSecurityService.ROLE_LOESCHEN, KontraktSecurityService.ROLE_ADMIN)

    old_status = contract.status
    if force and has_movements:
        db.delete(contract)
        action = "HARD_DELETE"
    else:
        contract.status = "GELOESCHT"
        contract.updated_by = user.get("sub")
        action = "SOFT_DELETE"
    KontraktAuditService(db).log_change(
        tenant_id=tenant_id, entity_type="kon_contract", entity_id=contract_id,
        field_name="status", action=action, changed_by=user.get("sub"),
        old_value=old_status, new_value="GELOESCHT" if action == "SOFT_DELETE" else None,
    )
    db.commit()
    return {"ok": True, "action": action}


@router.post("/{contract_id}/cancel", response_model=KontraktOut, summary="Kontrakt stornieren")
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
    audit = KontraktAuditService(db)
    audit.log_change(tenant_id=tenant_id, entity_type="kon_contract", entity_id=contract_id,
                     field_name="status", action="CANCEL", changed_by=user.get("sub"), old_value=old_status, new_value="STORNIERT")
    if reason:
        audit.log_change(tenant_id=tenant_id, entity_type="kon_contract", entity_id=contract_id,
                         field_name="cancel_reason", action="CANCEL", changed_by=user.get("sub"), old_value=None, new_value=reason)
    db.commit()
    return await get_kontrakt(contract_id, db, tenant_id, user)


# ── Movements ─────────────────────────────────────────────────────────────────

@router.get("/{contract_id}/movements", response_model=KontraktOut, summary="Kontrakt movements auflisten")
async def list_kontrakt_movements(
    contract_id: str,
    include_archived: bool = Query(False),
    only_invoiced: Optional[bool] = Query(None),
    article_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    _require_roles(user, KontraktSecurityService.ROLE_LESEN, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
    rows = db.query(KonContractMovement).filter(
        KonContractMovement.tenant_id == tenant_id, KonContractMovement.contract_id == contract_id
    ).order_by(KonContractMovement.movement_date.desc())
    if not include_archived:
        rows = rows.filter(KonContractMovement.is_archived.is_(False))
    if only_invoiced is not None:
        rows = rows.filter(KonContractMovement.is_invoiced.is_(only_invoiced))
    if article_id:
        line_ids = [r[0] for r in db.query(KonContractLine.line_id).filter(
            KonContractLine.tenant_id == tenant_id, KonContractLine.contract_id == contract_id,
            KonContractLine.article_id == article_id,
        ).all()]
        rows = rows.filter(KonContractMovement.line_id.in_(line_ids)) if line_ids else rows.filter(False)
    payload = [
        KonContractMovementOut(
            movement_id=r.movement_id, contract_id=r.contract_id, line_id=r.line_id,
            order_no=r.order_no, delivery_note_no=r.delivery_note_no, invoice_no=r.invoice_no,
            movement_date=r.movement_date, quantity=float(r.quantity or 0),
            unit_price=float(r.unit_price) if r.unit_price is not None else None,
            route_no=r.route_no, is_invoiced=bool(r.is_invoiced), is_archived=bool(r.is_archived),
        ).model_dump()
        for r in rows.all()
    ]
    verk_menge = sum(Decimal(str(r["quantity"])) for r in payload)
    return {"items": payload, "verk_menge": float(verk_menge)}


@router.post("/{contract_id}/movements", response_model=KontraktOut, summary="Kontrakt movement anlegen")
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
    line = db.query(KonContractLine).filter(
        KonContractLine.tenant_id == tenant_id, KonContractLine.contract_id == contract_id,
        KonContractLine.line_id == payload.line_id,
    ).first()
    if not line:
        raise HTTPException(status_code=404, detail="Contract line not found")

    rest_service = KontraktRestmengenService(db)
    rest = rest_service.compute_rest(tenant_id, contract_id)
    line_rest = rest.line_rest.get(payload.line_id, Decimal("0"))
    try:
        rest_service.enforce_overdelivery(bool(contract.allow_overdelivery), line_rest, Decimal(str(payload.quantity)))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    movement = KonContractMovement(
        movement_id=uuid7(), contract_id=contract_id, line_id=payload.line_id,
        order_no=payload.order_no, delivery_note_no=payload.delivery_note_no,
        invoice_no=payload.invoice_no, movement_date=payload.movement_date or datetime.utcnow(),
        quantity=payload.quantity, unit_price=payload.unit_price, route_no=payload.route_no,
        is_invoiced=payload.is_invoiced, is_archived=payload.is_archived,
        tenant_id=tenant_id, created_by=user.get("sub"),
    )
    db.add(movement)
    db.flush()
    rest_after = rest_service.compute_rest(tenant_id, contract_id)
    contract.status = KontraktRestmengenService.determine_status_from_rest(
        bool(contract.allow_overdelivery), contract.status or "OFFEN", rest_after.contract_rest,
    )
    contract.updated_by = user.get("sub")
    KontraktAuditService(db).log_change(
        tenant_id=tenant_id, entity_type="kon_contract_movement", entity_id=contract_id,
        field_name="quantity", action="CREATE", changed_by=user.get("sub"), old_value=None, new_value=payload.quantity,
    )
    db.commit()
    db.refresh(movement)
    return KonContractMovementOut(
        movement_id=movement.movement_id, contract_id=movement.contract_id, line_id=movement.line_id,
        order_no=movement.order_no, delivery_note_no=movement.delivery_note_no, invoice_no=movement.invoice_no,
        movement_date=movement.movement_date, quantity=float(movement.quantity or 0),
        unit_price=float(movement.unit_price) if movement.unit_price is not None else None,
        route_no=movement.route_no, is_invoiced=bool(movement.is_invoiced), is_archived=bool(movement.is_archived),
    ).model_dump()


# ── Audit ─────────────────────────────────────────────────────────────────────

@router.get("/{contract_id}/audit", response_model=KontraktOut, summary="Kontrakt audit auflisten")
async def list_kontrakt_audit(
    contract_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    _require_roles(user, KontraktSecurityService.ROLE_LESEN, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
    exists = db.query(func.count()).select_from(KonContract).filter(
        KonContract.tenant_id == tenant_id, KonContract.contract_id == contract_id
    ).scalar()
    if not exists:
        raise HTTPException(status_code=404, detail="Contract not found")
    from app.domains.operations.models import KonAuditLog
    logs = db.query(KonAuditLog).filter(
        KonAuditLog.tenant_id == tenant_id, KonAuditLog.entity_id == contract_id
    ).order_by(KonAuditLog.changed_at.desc()).all()
    return {"items": [
        {"audit_id": l.audit_id, "entity_type": l.entity_type, "entity_id": l.entity_id,
         "field_name": l.field_name, "old_value": l.old_value, "new_value": l.new_value,
         "action": l.action, "changed_at": l.changed_at, "changed_by": l.changed_by}
        for l in logs
    ]}


# ── Amendments (NOTE: /amendment-templates MUST be before /{contract_id}/amendments) ──

@router.get("/amendment-templates", response_model=KontraktOut, summary="Amendment templates auflisten")
async def list_amendment_templates(
    activeOnly: bool = Query(True),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    _require_roles(user, KontraktSecurityService.ROLE_LESEN, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
    q = db.query(AmendmentTemplate)
    if activeOnly:
        q = q.filter(AmendmentTemplate.is_active.is_(True))
    templates = q.order_by(AmendmentTemplate.name.asc()).all()
    return {"items": [AmendmentTemplateResponse(
        id=t.id, code=t.code, name=t.name, description=t.description,
        body_markdown=t.body_markdown, sections_schema=t.sections_schema,
        is_active=t.is_active, created_at=t.created_at,
    ).model_dump() for t in templates]}


@router.get("/{contract_id}/amendments", response_model=KontraktOut, summary="Amendments auflisten")
async def list_amendments(
    contract_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    _require_roles(user, KontraktSecurityService.ROLE_LESEN, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
    if not db.query(KonContract).filter(KonContract.tenant_id == tenant_id, KonContract.contract_id == contract_id).first():
        raise HTTPException(status_code=404, detail="Contract not found")
    amendments = db.query(ContractAmendment).filter(
        ContractAmendment.tenant_id == tenant_id, ContractAmendment.contract_id == contract_id,
    ).order_by(ContractAmendment.created_at.desc()).all()
    return {"items": [AmendmentResponse(
        id=a.id, contract_id=a.contract_id, type=a.type, reason=a.reason, status=a.status,
        changes=a.changes or {}, tenant_id=a.tenant_id, created_by=a.created_by, created_at=a.created_at,
    ).model_dump() for a in amendments]}


@router.post("/{contract_id}/amendments", status_code=201, response_model=KontraktOut, summary="Amendment anlegen")
async def create_amendment(
    contract_id: str,
    payload: AmendmentCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    _require_roles(user, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
    if not db.query(KonContract).filter(KonContract.tenant_id == tenant_id, KonContract.contract_id == contract_id).first():
        raise HTTPException(status_code=404, detail="Contract not found")
    amendment = ContractAmendment(
        id=uuid7(), contract_id=contract_id, type=payload.type, reason=payload.reason,
        status="pending", changes=payload.changes, tenant_id=tenant_id,
        created_by=user.get("sub") or payload.created_by,
    )
    db.add(amendment)
    db.flush()
    KontraktAuditService(db).log_change(
        tenant_id=tenant_id, entity_type="contract_amendment", entity_id=contract_id,
        field_name="type", action="CREATE", changed_by=user.get("sub"), old_value=None, new_value=payload.type,
    )
    db.commit()
    db.refresh(amendment)
    return AmendmentResponse(
        id=amendment.id, contract_id=amendment.contract_id, type=amendment.type,
        reason=amendment.reason, status=amendment.status, changes=amendment.changes or {},
        tenant_id=amendment.tenant_id, created_by=amendment.created_by, created_at=amendment.created_at,
    ).model_dump()


@router.patch("/{contract_id}/amendments/{amendment_id}", response_model=KontraktOut, summary="Amendment status aktualisieren")
async def update_amendment_status(
    contract_id: str,
    amendment_id: str,
    payload: AmendmentStatusUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    _require_roles(user, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
    amendment = db.query(ContractAmendment).filter(
        ContractAmendment.tenant_id == tenant_id, ContractAmendment.contract_id == contract_id,
        ContractAmendment.id == amendment_id,
    ).first()
    if not amendment:
        raise HTTPException(status_code=404, detail="Amendment not found")
    old_status = amendment.status
    amendment.status = payload.status
    KontraktAuditService(db).log_change(
        tenant_id=tenant_id, entity_type="contract_amendment", entity_id=contract_id,
        field_name="status", action="UPDATE", changed_by=user.get("sub"), old_value=old_status, new_value=payload.status,
    )
    db.commit()
    db.refresh(amendment)
    return AmendmentResponse(
        id=amendment.id, contract_id=amendment.contract_id, type=amendment.type,
        reason=amendment.reason, status=amendment.status, changes=amendment.changes or {},
        tenant_id=amendment.tenant_id, created_by=amendment.created_by, created_at=amendment.created_at,
    ).model_dump()


# ── Lookup ────────────────────────────────────────────────────────────────────

@router.post("/lookup/verkauf", response_model=KontraktOut, summary="Verkauf kontrakte lookup")
async def lookup_verkauf_kontrakte(
    query: Optional[str] = Body(default=None),
    only_open: bool = Body(default=True),
    limit: int = Body(default=50),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    _require_roles(user, KontraktSecurityService.ROLE_LESEN, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
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
        lines = db.query(KonContractLine).filter(
            KonContractLine.tenant_id == tenant_id, KonContractLine.contract_id == c.contract_id
        ).order_by(KonContractLine.position_no.asc()).all()
        for line in lines:
            result.append({
                "contract_id": c.contract_id, "line_id": line.line_id,
                "contract_no": c.contract_no, "position_no": line.position_no,
                "date": c.contract_date, "name": partner_name,
                "valid_from": c.valid_from, "valid_to": c.valid_to,
                "article_id": line.article_id,
                "bezeichnung": article_lookup.get_label(line.article_id, line.description1),
            })
    return {"items": result}


# ── Positionsmonitor ──────────────────────────────────────────────────────────

@router.get("/positionen", response_model=KontraktOut, summary="Positionen abrufen")
def get_positionen(
    article_ids: Optional[str] = Query(None, description="Komma-separierte Artikel-IDs"),
    include_done: bool = Query(False),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    """Rohwaren-Positionsmonitor: Long/Short pro Artikel."""
    from app.services.kontrakt_position_service import KontraktPositionService
    ids = [a.strip() for a in article_ids.split(",") if a.strip()] if article_ids else None
    return KontraktPositionService(db).compute_positions(tenant_id, article_ids=ids, include_done=include_done).to_dict()


# ── Dispositionen ─────────────────────────────────────────────────────────────

@router.get("/{kontrakt_id}/dispositionen", response_model=list[KontraktOut], summary="Dispositionen auflisten")
async def list_dispositionen(
    kontrakt_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    _require_roles(user, KontraktSecurityService.ROLE_LESEN, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
    try:
        return list_dispositionen_db(db, kontrakt_id)
    except Exception as e:
        err = str(e).lower()
        if "relation" in err or "does not exist" in err:
            return []
        raise HTTPException(status_code=503, detail=f"DB-Fehler: {e}",
                            headers={"X-Migration-Hint": "Run: alembic upgrade head"})


@router.post("/{kontrakt_id}/dispositionen", response_model=KontraktOut, status_code=201, summary="Disposition anlegen")
async def create_disposition(
    kontrakt_id: str,
    payload: DispositionCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    _require_roles(user, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
    try:
        return create_disposition_db(db, kontrakt_id, payload)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"DB-Fehler: {e}",
                            headers={"X-Migration-Hint": "Run: alembic upgrade head"})


@router.patch("/{kontrakt_id}/dispositionen/{disp_id}/freigabe", response_model=KontraktOut, summary="Disposition freigabe")
async def freigabe_disposition(
    kontrakt_id: str, disp_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    _require_roles(user, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
    from sqlalchemy import text as _sql_text
    try:
        result = db.execute(_sql_text(
            "UPDATE domain_agrar.kontrakt_dispositionen SET freigabe = true, status = 'FREIGEGEBEN', updated_at = now() "
            "WHERE id = :id AND kontrakt_id = :kid RETURNING id, status"
        ), {"id": disp_id, "kid": kontrakt_id}).fetchone()
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"DB-Fehler: {e}")
    if result is None:
        raise HTTPException(status_code=404, detail=f"Disposition {disp_id} nicht gefunden")
    return {"id": result[0], "status": result[1]}


@router.patch("/{kontrakt_id}/dispositionen/{disp_id}/geliefert", response_model=KontraktOut, summary="Disposition geliefert")
async def geliefert_disposition(
    kontrakt_id: str, disp_id: str,
    wiegeschein_nr: Optional[str] = Body(default=None, embed=True),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    _require_roles(user, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
    from sqlalchemy import text as _sql_text
    try:
        if wiegeschein_nr:
            result = db.execute(_sql_text(
                "UPDATE domain_agrar.kontrakt_dispositionen SET status = 'GELIEFERT', wiegeschein_nr = :ws, updated_at = now() "
                "WHERE id = :id AND kontrakt_id = :kid RETURNING id, status, wiegeschein_nr"
            ), {"id": disp_id, "kid": kontrakt_id, "ws": wiegeschein_nr}).fetchone()
        else:
            result = db.execute(_sql_text(
                "UPDATE domain_agrar.kontrakt_dispositionen SET status = 'GELIEFERT', updated_at = now() "
                "WHERE id = :id AND kontrakt_id = :kid RETURNING id, status, wiegeschein_nr"
            ), {"id": disp_id, "kid": kontrakt_id}).fetchone()
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"DB-Fehler: {e}")
    if result is None:
        raise HTTPException(status_code=404, detail=f"Disposition {disp_id} nicht gefunden")
    return {"id": result[0], "status": result[1], "wiegeschein_nr": result[2]}


@router.delete("/{kontrakt_id}/dispositionen/{disp_id}", response_model=KontraktOut, summary="Disposition storniere")
async def storniere_disposition(
    kontrakt_id: str, disp_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    _require_roles(user, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
    from sqlalchemy import text as _sql_text
    try:
        result = db.execute(_sql_text(
            "UPDATE domain_agrar.kontrakt_dispositionen SET status = 'STORNIERT', updated_at = now() "
            "WHERE id = :id AND kontrakt_id = :kid RETURNING id, status"
        ), {"id": disp_id, "kid": kontrakt_id}).fetchone()
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"DB-Fehler: {e}")
    if result is None:
        raise HTTPException(status_code=404, detail=f"Disposition {disp_id} nicht gefunden")
    return {"id": result[0], "status": result[1]}
