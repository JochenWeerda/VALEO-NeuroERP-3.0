from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Literal, Optional

from app.services.position_guard_service import PositionGuardService

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, text as _sql_text
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
)

router = APIRouter(prefix="/kontrakte", tags=["kontrakte"])

ContractType = Literal["EINKAUF", "ZUKAUF", "VERKAUF"]
StatusType = Literal["OFFEN", "ERLEDIGT", "STORNIERT", "GELOESCHT"]
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


def _num(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _text(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _iso(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return _text(value)


def _date(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    text = _text(value)
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "ja", "y"}
    return bool(value)


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        result = []
        for item in value:
            text = _text(item)
            if text:
                result.append(text)
        return result
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return []


def _contract_reference_price(contract: KonContract, first_line_price: Optional[float]) -> Optional[float]:
    if first_line_price is not None and first_line_price > 0:
        return first_line_price
    if contract.min_price is not None:
        return float(contract.min_price)
    return None


def _build_contract_steering(
    contract: KonContract,
    contract_rest: Decimal,
    first_line_price: Optional[float] = None,
) -> dict[str, Any]:
    conditions = contract.conditions_json or {}

    hedge_quantity_t = _num(conditions.get("hedge_quantity_t"))
    hedge_target_pct = _num(conditions.get("hedge_target_pct"))
    market_price_eur_t = _num(conditions.get("market_price_eur_t"))
    reference_price = _contract_reference_price(contract, first_line_price)
    rest_quantity = float(contract_rest)

    hedge_quote_pct = None
    if hedge_quantity_t is not None:
        total_qty = float(contract.total_quantity or 0)
        if total_qty > 0:
            hedge_quote_pct = min(100.0, (hedge_quantity_t / total_qty) * 100.0)

    hedge_gap_pct = None
    if hedge_target_pct is not None:
        hedge_gap_pct = round(max(0.0, hedge_target_pct - float(hedge_quote_pct or 0.0)), 2)

    market_price_delta_eur_t = None
    market_valuation_eur = None
    if market_price_eur_t is not None and reference_price is not None:
        market_price_delta_eur_t = round(market_price_eur_t - reference_price, 2)
        market_valuation_eur = round(market_price_delta_eur_t * rest_quantity, 2)

    dunning_level = int(_num(conditions.get("dunning_level")) or 0)
    dunning_blocked = _bool(conditions.get("dunning_blocked"))
    alternate_articles = _string_list(conditions.get("alternate_articles"))
    washout_quantity_t = _num(conditions.get("washout_quantity_t"))
    writeoff_quantity_t = _num(conditions.get("writeoff_quantity_t"))
    print_copy_count = int(_num(conditions.get("print_copy_count")) or 0)
    today = datetime.now(timezone.utc)
    dunning_due_at = _date(conditions.get("dunning_due_at")) or contract.valid_to
    dunning_candidate = bool(
        contract.status == "OFFEN"
        and not dunning_blocked
        and rest_quantity > 0
        and dunning_due_at is not None
        and dunning_due_at < today
    )

    return {
        "contract_class": _text(conditions.get("contract_class")),
        "contract_group": _text(conditions.get("contract_group")),
        "contract_variant": _text(conditions.get("contract_variant")),
        "disposition_flag": _text(conditions.get("disposition_flag")),
        "parity_code": _text(conditions.get("parity_code")),
        "parity_label": _text(conditions.get("parity_label")),
        "fallback_route": _text(conditions.get("fallback_route")),
        "alternate_articles": alternate_articles,
        "print_template": _text(conditions.get("print_template")),
        "print_channel": _text(conditions.get("print_channel")),
        "print_copy_count": print_copy_count,
        "last_printed_at": _iso(conditions.get("last_printed_at")),
        "print_ready": bool(_text(conditions.get("print_template")) and _text(conditions.get("print_channel"))),
        "washout_status": _text(conditions.get("washout_status")),
        "washout_quantity_t": washout_quantity_t,
        "washout_reason": _text(conditions.get("washout_reason")),
        "writeoff_quantity_t": writeoff_quantity_t,
        "writeoff_reason": _text(conditions.get("writeoff_reason")),
        "writeoff_candidate": bool((writeoff_quantity_t or 0) > 0 or (washout_quantity_t or 0) > 0),
        "hedge_strategy": _text(conditions.get("hedge_strategy")),
        "hedge_market": _text(conditions.get("hedge_market")),
        "hedge_status": _text(conditions.get("hedge_status")),
        "hedge_target_pct": hedge_target_pct,
        "hedge_quantity_t": hedge_quantity_t,
        "hedge_quote_pct": hedge_quote_pct,
        "hedge_gap_pct": hedge_gap_pct,
        "market_price_source": _text(conditions.get("market_price_source")),
        "market_price_eur_t": market_price_eur_t,
        "market_price_date": _iso(conditions.get("market_price_date")),
        "market_price_delta_eur_t": market_price_delta_eur_t,
        "market_valuation_eur": market_valuation_eur,
        "reference_price_eur_t": reference_price,
        "dunning_level": dunning_level,
        "dunning_blocked": dunning_blocked,
        "dunning_due_at": _iso(dunning_due_at),
        "dunning_last_at": _iso(conditions.get("dunning_last_at")),
        "dunning_candidate": dunning_candidate,
        "dunning_reason": _text(conditions.get("dunning_reason")),
    }


def _contract_to_out(contract: KonContract, line_out: list[dict[str, Any]], contract_rest: Decimal) -> dict[str, Any]:
    first_line_price = None
    if line_out:
        first_line_price = _num(line_out[0].get("unit_price"))
    steering = _build_contract_steering(contract, contract_rest, first_line_price)
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
        "steering": steering,
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
        first_line = (
            db.query(KonContractLine)
            .filter(KonContractLine.contract_id == c.contract_id, KonContractLine.tenant_id == tenant_id)
            .order_by(KonContractLine.position_no.asc())
            .first()
        )
        party_name = party_adapter.get_name(c.party_id)
        first_unit_price = float(first_line.unit_price) if first_line and first_line.unit_price is not None else None
        steering = _build_contract_steering(c, rest.contract_rest, first_unit_price)
        payload.append(
            {
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

    if payload.contract_type == "VERKAUF" and payload.lines:
        period_dt = payload.valid_to or payload.valid_from
        if period_dt:
            period_key = period_dt.strftime("%Y-%m") if hasattr(period_dt, "strftime") else None
            if period_key:
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

    if payload.lines and contract.contract_type == "VERKAUF":
        period_dt = contract.valid_to or contract.valid_from
        if period_dt:
            period_key = period_dt.strftime("%Y-%m") if hasattr(period_dt, "strftime") else None
            if period_key:
                guard = PositionGuardService(db)
                by_article: dict[str, Decimal] = defaultdict(Decimal)
                for line_in in payload.lines:
                    by_article[line_in.article_id] += Decimal(str(line_in.qty_contract))
                for aid, delta in by_article.items():
                    result = guard.check_impact(
                        tenant_id=tenant_id,
                        branch_id=contract.branch_id,
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


@router.put("/{contract_id}")
async def replace_kontrakt(
    contract_id: str,
    payload: KonContractIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    """Full replacement — delegates to PATCH logic (PATCH already accepts all fields)."""
    return await update_kontrakt(contract_id, payload, db, tenant_id, user)


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
            raise HTTPException(
                status_code=409,
                detail="Kontrakt hat Umsaetze/Movements. Loeschung nur mit force=true (KONTRAKT_ADMIN).",
            )
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
        tenant_id=tenant_id,
        entity_type="kon_contract",
        entity_id=contract_id,
        field_name="status",
        action=action,
        changed_by=user.get("sub"),
        old_value=old_status,
        new_value="GELOESCHT" if action == "SOFT_DELETE" else None,
    )
    db.commit()
    return {"ok": True, "action": action}


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
                "audit_id": line_item.audit_id,
                "entity_type": line_item.entity_type,
                "entity_id": line_item.entity_id,
                "field_name": line_item.field_name,
                "old_value": line_item.old_value,
                "new_value": line_item.new_value,
                "action": line_item.action,
                "changed_at": line_item.changed_at,
                "changed_by": line_item.changed_by,
            }
            for line_item in logs
        ]
    }


# ===========================================================================
# AMENDMENTS — Vertragsänderungen & Vorlagen
# NOTE: /amendment-templates MUST be defined BEFORE /{contract_id}/amendments
#       to avoid FastAPI treating "amendment-templates" as a path param.
# ===========================================================================

class AmendmentCreate(BaseModel):
    type: str
    reason: str
    changes: dict = {}
    created_by: str = "system"


class AmendmentResponse(BaseModel):
    id: str
    contract_id: str
    type: str
    reason: str
    status: str
    changes: dict
    tenant_id: str
    created_by: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AmendmentTemplateResponse(BaseModel):
    id: str
    code: str
    name: str
    description: Optional[str]
    body_markdown: Optional[str]
    sections_schema: Optional[dict]
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AmendmentStatusUpdate(BaseModel):
    status: Literal["approved", "rejected"]


@router.get("/amendment-templates")
async def list_amendment_templates(
    activeOnly: bool = Query(True),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    """Listet Vorlagen für Vertragsänderungen."""
    _require_roles(
        user,
        KontraktSecurityService.ROLE_LESEN,
        KontraktSecurityService.ROLE_BEARBEITEN,
        KontraktSecurityService.ROLE_ADMIN,
    )
    q = db.query(AmendmentTemplate)
    if activeOnly:
        q = q.filter(AmendmentTemplate.is_active.is_(True))
    templates = q.order_by(AmendmentTemplate.name.asc()).all()
    return {
        "items": [
            AmendmentTemplateResponse(
                id=t.id,
                code=t.code,
                name=t.name,
                description=t.description,
                body_markdown=t.body_markdown,
                sections_schema=t.sections_schema,
                is_active=t.is_active,
                created_at=t.created_at,
            ).model_dump()
            for t in templates
        ]
    }


@router.get("/{contract_id}/amendments")
async def list_amendments(
    contract_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    """Listet alle Änderungen (Amendments) zu einem Kontrakt."""
    _require_roles(
        user,
        KontraktSecurityService.ROLE_LESEN,
        KontraktSecurityService.ROLE_BEARBEITEN,
        KontraktSecurityService.ROLE_ADMIN,
    )
    contract = (
        db.query(KonContract)
        .filter(KonContract.tenant_id == tenant_id, KonContract.contract_id == contract_id)
        .first()
    )
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    amendments = (
        db.query(ContractAmendment)
        .filter(
            ContractAmendment.tenant_id == tenant_id,
            ContractAmendment.contract_id == contract_id,
        )
        .order_by(ContractAmendment.created_at.desc())
        .all()
    )
    return {
        "items": [
            AmendmentResponse(
                id=a.id,
                contract_id=a.contract_id,
                type=a.type,
                reason=a.reason,
                status=a.status,
                changes=a.changes or {},
                tenant_id=a.tenant_id,
                created_by=a.created_by,
                created_at=a.created_at,
            ).model_dump()
            for a in amendments
        ]
    }


@router.post("/{contract_id}/amendments", status_code=201)
async def create_amendment(
    contract_id: str,
    payload: AmendmentCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    """Legt eine neue Vertragsänderung (Amendment) an."""
    _require_roles(user, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
    contract = (
        db.query(KonContract)
        .filter(KonContract.tenant_id == tenant_id, KonContract.contract_id == contract_id)
        .first()
    )
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    amendment = ContractAmendment(
        id=uuid7(),
        contract_id=contract_id,
        type=payload.type,
        reason=payload.reason,
        status="pending",
        changes=payload.changes,
        tenant_id=tenant_id,
        created_by=user.get("sub") or payload.created_by,
    )
    db.add(amendment)
    db.flush()

    KontraktAuditService(db).log_change(
        tenant_id=tenant_id,
        entity_type="contract_amendment",
        entity_id=contract_id,
        field_name="type",
        action="CREATE",
        changed_by=user.get("sub"),
        old_value=None,
        new_value=payload.type,
    )
    db.commit()
    db.refresh(amendment)
    return AmendmentResponse(
        id=amendment.id,
        contract_id=amendment.contract_id,
        type=amendment.type,
        reason=amendment.reason,
        status=amendment.status,
        changes=amendment.changes or {},
        tenant_id=amendment.tenant_id,
        created_by=amendment.created_by,
        created_at=amendment.created_at,
    ).model_dump()


@router.patch("/{contract_id}/amendments/{amendment_id}")
async def update_amendment_status(
    contract_id: str,
    amendment_id: str,
    payload: AmendmentStatusUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    """Aktualisiert den Status eines Amendments (pending → approved / rejected)."""
    _require_roles(user, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
    amendment = (
        db.query(ContractAmendment)
        .filter(
            ContractAmendment.tenant_id == tenant_id,
            ContractAmendment.contract_id == contract_id,
            ContractAmendment.id == amendment_id,
        )
        .first()
    )
    if not amendment:
        raise HTTPException(status_code=404, detail="Amendment not found")

    old_status = amendment.status
    amendment.status = payload.status

    KontraktAuditService(db).log_change(
        tenant_id=tenant_id,
        entity_type="contract_amendment",
        entity_id=contract_id,
        field_name="status",
        action="UPDATE",
        changed_by=user.get("sub"),
        old_value=old_status,
        new_value=payload.status,
    )
    db.commit()
    db.refresh(amendment)
    return AmendmentResponse(
        id=amendment.id,
        contract_id=amendment.contract_id,
        type=amendment.type,
        reason=amendment.reason,
        status=amendment.status,
        changes=amendment.changes or {},
        tenant_id=amendment.tenant_id,
        created_by=amendment.created_by,
        created_at=amendment.created_at,
    ).model_dump()


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


# ---------------------------------------------------------------------------
# Long/Short-Positionsmonitor
# ---------------------------------------------------------------------------

@router.get("/positionen")
def get_positionen(  # noqa: E302
    article_ids: Optional[str] = Query(None, description="Komma-separierte Artikel-IDs"),
    include_done: bool = Query(False, description="Erledigte Kontrakte einbeziehen"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    """Rohwaren-Positionsmonitor: Long/Short pro Artikel.

    Zeigt Einkauf vs. Verkauf Restmengen und Deckungsgrad.
    SHORT = Unterdeckung (Verkaufskontrakte nicht gedeckt durch Einkauf).
    """
    from app.services.kontrakt_position_service import KontraktPositionService

    ids = [a.strip() for a in article_ids.split(",") if a.strip()] if article_ids else None
    service = KontraktPositionService(db)
    summary = service.compute_positions(tenant_id, article_ids=ids, include_done=include_done)
    return summary.to_dict()


# ===========================================================================
# KONTRAKT-DISPOSITION — Disposition als Sub-Ressource eines Kontrakts
# ===========================================================================

import uuid as _uuid_mod
import json as _json_mod


class DispositionCreate(BaseModel):
    kontrakt_nr: str
    kontrakt_pos_nr: int = 1
    geplantes_lieferdatum: Optional[str] = None
    lieferdatum: Optional[str] = None
    menge: float
    freigabe: bool = False
    wiegeschein_nr: Optional[str] = None
    bemerkung: Optional[str] = None


class DispositionOut(DispositionCreate):
    id: str
    disposition_nr: int
    status: str  # OFFEN / FREIGEGEBEN / GELIEFERT / STORNIERT


def _ensure_disposition_table(db: Session) -> None:
    """Erstellt domain_agrar.kontrakt_dispositionen falls die Tabelle fehlt."""
    try:
        db.execute(
            _sql_text(
                """
                CREATE TABLE IF NOT EXISTS domain_agrar.kontrakt_dispositionen (
                    id               TEXT PRIMARY KEY,
                    kontrakt_id      TEXT NOT NULL,
                    disposition_nr   INTEGER NOT NULL,
                    kontrakt_nr      TEXT NOT NULL,
                    kontrakt_pos_nr  INTEGER NOT NULL DEFAULT 1,
                    geplantes_lieferdatum TEXT,
                    lieferdatum      TEXT,
                    menge            NUMERIC(18,3) NOT NULL,
                    freigabe         BOOLEAN NOT NULL DEFAULT FALSE,
                    wiegeschein_nr   TEXT,
                    bemerkung        TEXT,
                    status           TEXT NOT NULL DEFAULT 'OFFEN',
                    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
                    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
        )
        db.commit()
    except Exception:
        db.rollback()


@router.get("/{kontrakt_id}/dispositionen", response_model=list)
async def list_dispositionen(
    kontrakt_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    """Listet alle Dispositionen zu einem Kontrakt."""
    _require_roles(
        user,
        KontraktSecurityService.ROLE_LESEN,
        KontraktSecurityService.ROLE_BEARBEITEN,
        KontraktSecurityService.ROLE_ADMIN,
    )
    try:
        rows = db.execute(
            _sql_text(
                "SELECT id, kontrakt_id, disposition_nr, kontrakt_nr, kontrakt_pos_nr, "
                "geplantes_lieferdatum, lieferdatum, menge, freigabe, wiegeschein_nr, "
                "bemerkung, status, created_at, updated_at "
                "FROM domain_agrar.kontrakt_dispositionen "
                "WHERE kontrakt_id = :kid ORDER BY disposition_nr ASC"
            ),
            {"kid": kontrakt_id},
        ).fetchall()
    except Exception as e:
        err = str(e).lower()
        if "relation" in err or "does not exist" in err:
            return []
        raise HTTPException(
            status_code=503,
            detail=f"DB-Fehler: {e}",
            headers={"X-Migration-Hint": "Run: alembic upgrade head (kontrakt_dispositionen fehlt)"},
        )
    return [
        {
            "id": r[0],
            "kontrakt_id": r[1],
            "disposition_nr": r[2],
            "kontrakt_nr": r[3],
            "kontrakt_pos_nr": r[4],
            "geplantes_lieferdatum": r[5],
            "lieferdatum": r[6],
            "menge": float(r[7]) if r[7] is not None else None,
            "freigabe": bool(r[8]),
            "wiegeschein_nr": r[9],
            "bemerkung": r[10],
            "status": r[11],
            "created_at": r[12].isoformat() if r[12] else None,
            "updated_at": r[13].isoformat() if r[13] else None,
        }
        for r in rows
    ]


@router.post("/{kontrakt_id}/dispositionen", response_model=dict, status_code=201)
async def create_disposition(
    kontrakt_id: str,
    payload: DispositionCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    """Legt eine neue Disposition zu einem Kontrakt an."""
    _require_roles(user, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)

    _ensure_disposition_table(db)

    new_id = str(_uuid_mod.uuid4())
    try:
        db.execute(
            _sql_text(
                """
                INSERT INTO domain_agrar.kontrakt_dispositionen (
                    id, kontrakt_id, disposition_nr, kontrakt_nr, kontrakt_pos_nr,
                    geplantes_lieferdatum, lieferdatum, menge, freigabe,
                    wiegeschein_nr, bemerkung, status, created_at, updated_at
                ) VALUES (
                    :id, :kontrakt_id,
                    COALESCE((SELECT MAX(disposition_nr) FROM domain_agrar.kontrakt_dispositionen
                               WHERE kontrakt_id = :kontrakt_id), 0) + 1,
                    :kontrakt_nr, :kontrakt_pos_nr,
                    :geplantes_lieferdatum, :lieferdatum, :menge, :freigabe,
                    :wiegeschein_nr, :bemerkung,
                    CASE WHEN :freigabe THEN 'FREIGEGEBEN' ELSE 'OFFEN' END,
                    now(), now()
                )
                """
            ),
            {
                "id": new_id,
                "kontrakt_id": kontrakt_id,
                "kontrakt_nr": payload.kontrakt_nr,
                "kontrakt_pos_nr": payload.kontrakt_pos_nr,
                "geplantes_lieferdatum": payload.geplantes_lieferdatum,
                "lieferdatum": payload.lieferdatum,
                "menge": payload.menge,
                "freigabe": payload.freigabe,
                "wiegeschein_nr": payload.wiegeschein_nr,
                "bemerkung": payload.bemerkung,
            },
        )
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail=f"DB-Fehler: {e}",
            headers={"X-Migration-Hint": "Run: alembic upgrade head"},
        )

    # Fetch the created record to return disposition_nr
    row = db.execute(
        _sql_text(
            "SELECT id, disposition_nr, status FROM domain_agrar.kontrakt_dispositionen WHERE id = :id"
        ),
        {"id": new_id},
    ).fetchone()
    return {
        "id": row[0] if row else new_id,
        "kontrakt_id": kontrakt_id,
        "disposition_nr": row[1] if row else 1,
        "kontrakt_nr": payload.kontrakt_nr,
        "kontrakt_pos_nr": payload.kontrakt_pos_nr,
        "menge": payload.menge,
        "freigabe": payload.freigabe,
        "status": row[2] if row else ("FREIGEGEBEN" if payload.freigabe else "OFFEN"),
    }


@router.patch("/{kontrakt_id}/dispositionen/{disp_id}/freigabe", response_model=dict)
async def freigabe_disposition(
    kontrakt_id: str,
    disp_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    """Setzt freigabe=true und status=FREIGEGEBEN für eine Disposition."""
    _require_roles(user, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
    try:
        result = db.execute(
            _sql_text(
                "UPDATE domain_agrar.kontrakt_dispositionen "
                "SET freigabe = true, status = 'FREIGEGEBEN', updated_at = now() "
                "WHERE id = :id AND kontrakt_id = :kid "
                "RETURNING id, status"
            ),
            {"id": disp_id, "kid": kontrakt_id},
        ).fetchone()
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"DB-Fehler: {e}")
    if result is None:
        raise HTTPException(status_code=404, detail=f"Disposition {disp_id} nicht gefunden")
    return {"id": result[0], "status": result[1]}


@router.patch("/{kontrakt_id}/dispositionen/{disp_id}/geliefert", response_model=dict)
async def geliefert_disposition(
    kontrakt_id: str,
    disp_id: str,
    wiegeschein_nr: Optional[str] = Body(default=None, embed=True),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    """Setzt status=GELIEFERT und optional wiegeschein_nr für eine Disposition."""
    _require_roles(user, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
    try:
        if wiegeschein_nr:
            result = db.execute(
                _sql_text(
                    "UPDATE domain_agrar.kontrakt_dispositionen "
                    "SET status = 'GELIEFERT', wiegeschein_nr = :ws, updated_at = now() "
                    "WHERE id = :id AND kontrakt_id = :kid "
                    "RETURNING id, status, wiegeschein_nr"
                ),
                {"id": disp_id, "kid": kontrakt_id, "ws": wiegeschein_nr},
            ).fetchone()
        else:
            result = db.execute(
                _sql_text(
                    "UPDATE domain_agrar.kontrakt_dispositionen "
                    "SET status = 'GELIEFERT', updated_at = now() "
                    "WHERE id = :id AND kontrakt_id = :kid "
                    "RETURNING id, status, wiegeschein_nr"
                ),
                {"id": disp_id, "kid": kontrakt_id},
            ).fetchone()
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"DB-Fehler: {e}")
    if result is None:
        raise HTTPException(status_code=404, detail=f"Disposition {disp_id} nicht gefunden")
    return {"id": result[0], "status": result[1], "wiegeschein_nr": result[2]}


@router.delete("/{kontrakt_id}/dispositionen/{disp_id}", response_model=dict)
async def storniere_disposition(
    kontrakt_id: str,
    disp_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    user: User = Depends(get_current_user),
):
    """Soft-Delete: Setzt status=STORNIERT für eine Disposition."""
    _require_roles(user, KontraktSecurityService.ROLE_BEARBEITEN, KontraktSecurityService.ROLE_ADMIN)
    try:
        result = db.execute(
            _sql_text(
                "UPDATE domain_agrar.kontrakt_dispositionen "
                "SET status = 'STORNIERT', updated_at = now() "
                "WHERE id = :id AND kontrakt_id = :kid "
                "RETURNING id, status"
            ),
            {"id": disp_id, "kid": kontrakt_id},
        ).fetchone()
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"DB-Fehler: {e}")
    if result is None:
        raise HTTPException(status_code=404, detail=f"Disposition {disp_id} nicht gefunden")
    return {"id": result[0], "status": result[1]}
