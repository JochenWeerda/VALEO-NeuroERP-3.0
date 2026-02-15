"""
Agrar self-billing settlements with deduction and posting workflow (AGRAR-SET-01).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.documents.router_helpers import get_repository, save_to_store
from app.infrastructure.models import AgrarSettlement, AgrarSettlementDeduction
from modules.agrar.services.moisture_engine import MoistureEngineInput, calculate_billing_weight
from modules.agrar.services.settlement_calculator import (
    calc_deduction_amount as _calc_deduction_amount_impl,
    compute_settlement_amounts as _compute_settlement_amounts_impl,
    round_money as _round_money_impl,
    round_qty as _round_qty_impl,
)

router = APIRouter()

DeductionType = Literal["drying", "cleaning", "freight", "other"]
DeductionMode = Literal["per_ton", "fixed"]
SettlementStatus = Literal["draft", "posted", "cancelled"]


def _round_money(value: Decimal | float | int) -> Decimal:
    return _round_money_impl(value)


def _round_qty(value: Decimal | float | int) -> Decimal:
    return _round_qty_impl(value)


class DeductionInput(BaseModel):
    deduction_type: DeductionType
    mode: DeductionMode
    rate_per_ton_eur: Optional[float] = Field(default=None, ge=0)
    fixed_amount_eur: Optional[float] = Field(default=None, ge=0)
    basis_quantity_tons: Optional[float] = Field(default=None, ge=0)
    note: Optional[str] = None

    @model_validator(mode="after")
    def validate_mode_fields(self):
        if self.mode == "per_ton" and self.rate_per_ton_eur is None:
            raise ValueError("rate_per_ton_eur is required for mode=per_ton")
        if self.mode == "fixed" and self.fixed_amount_eur is None:
            raise ValueError("fixed_amount_eur is required for mode=fixed")
        return self


class SettlementCreate(BaseModel):
    settlement_number: Optional[str] = Field(default=None, min_length=3, max_length=50)
    contract_id: Optional[str] = None
    ticket_id: Optional[str] = None
    supplier_id: str
    article_id: Optional[str] = None
    gross_quantity_kg: float = Field(..., gt=0)
    billing_quantity_kg: Optional[float] = Field(default=None, gt=0)
    unit_price_eur_per_ton: float = Field(..., gt=0)
    deductions: list[DeductionInput] = Field(default_factory=list)
    note: Optional[str] = None


class SettlementPostRequest(BaseModel):
    debit_account: str = Field(default="5000", min_length=3, max_length=20)
    credit_account_supplier: str = Field(default="3300", min_length=3, max_length=20)
    credit_account_deductions: str = Field(default="5490", min_length=3, max_length=20)
    posting_date: Optional[datetime] = None


class BillingWeightPreviewRequest(BaseModel):
    net_weight_kg: float = Field(..., gt=0)
    moisture_pct: float = Field(..., ge=0, lt=100)
    impurities_pct: float = Field(default=0.0, ge=0, lt=100)
    target_moisture_pct: float = Field(default=14.0, ge=0, lt=100)
    base_impurities_pct: float = Field(default=2.0, ge=0, lt=100)
    allow_bonus: bool = False


class DeductionOut(BaseModel):
    id: str
    deduction_type: DeductionType
    mode: DeductionMode
    rate_per_ton_eur: Optional[float] = None
    fixed_amount_eur: Optional[float] = None
    basis_quantity_tons: Optional[float] = None
    amount_eur: float
    note: Optional[str] = None


class SettlementOut(BaseModel):
    id: str
    settlement_number: str
    contract_id: Optional[str] = None
    ticket_id: Optional[str] = None
    supplier_id: str
    article_id: Optional[str] = None
    gross_quantity_kg: float
    billing_quantity_kg: float
    unit_price_eur_per_ton: float
    gross_amount_eur: float
    total_deductions_eur: float
    net_amount_eur: float
    currency: str
    status: SettlementStatus
    posted_journal_ref: Optional[str] = None
    posted_at: Optional[datetime] = None
    note: Optional[str] = None
    deductions: list[DeductionOut] = Field(default_factory=list)


def _calc_deduction_amount(deduction: DeductionInput, billing_qty_tons: Decimal) -> Decimal:
    return _calc_deduction_amount_impl(deduction, billing_qty_tons)


def _compute_settlement_amounts(
    *,
    billing_quantity_kg: Decimal,
    unit_price_eur_per_ton: Decimal,
    deductions: list[DeductionInput],
) -> dict[str, Decimal]:
    result = _compute_settlement_amounts_impl(
        billing_quantity_kg=billing_quantity_kg,
        unit_price_eur_per_ton=unit_price_eur_per_ton,
        deductions=deductions,
    )
    net_amount = result["net_amount"]
    if net_amount < Decimal("0"):
        raise HTTPException(status_code=400, detail="Deductions exceed gross amount")
    return result


def _to_out(settlement: AgrarSettlement, deductions: list[AgrarSettlementDeduction]) -> SettlementOut:
    return SettlementOut(
        id=settlement.id,
        settlement_number=settlement.settlement_number,
        contract_id=settlement.contract_id,
        ticket_id=settlement.ticket_id,
        supplier_id=settlement.supplier_id,
        article_id=settlement.article_id,
        gross_quantity_kg=float(settlement.gross_quantity_kg),
        billing_quantity_kg=float(settlement.billing_quantity_kg),
        unit_price_eur_per_ton=float(settlement.unit_price_eur_per_ton),
        gross_amount_eur=float(settlement.gross_amount_eur),
        total_deductions_eur=float(settlement.total_deductions_eur),
        net_amount_eur=float(settlement.net_amount_eur),
        currency=settlement.currency,
        status=settlement.status,
        posted_journal_ref=settlement.posted_journal_ref,
        posted_at=settlement.posted_at,
        note=settlement.note,
        deductions=[
            DeductionOut(
                id=d.id,
                deduction_type=d.deduction_type,
                mode=d.mode,
                rate_per_ton_eur=float(d.rate_per_ton_eur) if d.rate_per_ton_eur is not None else None,
                fixed_amount_eur=float(d.fixed_amount_eur) if d.fixed_amount_eur is not None else None,
                basis_quantity_tons=float(d.basis_quantity_tons) if d.basis_quantity_tons is not None else None,
                amount_eur=float(d.amount_eur),
                note=d.note,
            )
            for d in deductions
        ],
    )


@router.post("/billing-weight/preview", response_model=dict)
async def preview_billing_weight(payload: BillingWeightPreviewRequest) -> dict:
    result = calculate_billing_weight(
        MoistureEngineInput(
            net_weight_kg=Decimal(str(payload.net_weight_kg)),
            moisture_pct=Decimal(str(payload.moisture_pct)),
            impurities_pct=Decimal(str(payload.impurities_pct)),
            target_moisture_pct=Decimal(str(payload.target_moisture_pct)),
            base_impurities_pct=Decimal(str(payload.base_impurities_pct)),
            allow_bonus=payload.allow_bonus,
        )
    )
    return {
        "net_weight_kg": float(result.net_weight_kg),
        "billing_weight_kg": float(result.billing_weight_kg),
        "deduction_kg": float(result.deduction_kg),
        "moisture_factor": float(result.moisture_factor),
        "impurities_factor": float(result.impurities_factor),
    }


@router.post("/preview", response_model=dict)
async def preview_settlement(payload: SettlementCreate):
    billing_qty = _round_qty(payload.billing_quantity_kg if payload.billing_quantity_kg is not None else payload.gross_quantity_kg)
    amounts = _compute_settlement_amounts(
        billing_quantity_kg=billing_qty,
        unit_price_eur_per_ton=Decimal(str(payload.unit_price_eur_per_ton)),
        deductions=payload.deductions,
    )
    return {
        "gross_quantity_kg": float(payload.gross_quantity_kg),
        "billing_quantity_kg": float(billing_qty),
        "gross_amount_eur": float(amounts["gross_amount"]),
        "total_deductions_eur": float(amounts["total_deductions"]),
        "net_amount_eur": float(amounts["net_amount"]),
    }


@router.post("/", response_model=SettlementOut, status_code=201)
async def create_settlement(
    payload: SettlementCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    settlement_number = payload.settlement_number or f"SET-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    duplicate = (
        db.query(AgrarSettlement)
        .filter(AgrarSettlement.tenant_id == tenant_id, AgrarSettlement.settlement_number == settlement_number)
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="settlement_number already exists")

    gross_qty = _round_qty(payload.gross_quantity_kg)
    billing_qty = _round_qty(payload.billing_quantity_kg if payload.billing_quantity_kg is not None else payload.gross_quantity_kg)
    amounts = _compute_settlement_amounts(
        billing_quantity_kg=billing_qty,
        unit_price_eur_per_ton=Decimal(str(payload.unit_price_eur_per_ton)),
        deductions=payload.deductions,
    )

    settlement = AgrarSettlement(
        id=str(uuid.uuid4()),
        settlement_number=settlement_number,
        contract_id=payload.contract_id,
        ticket_id=payload.ticket_id,
        supplier_id=payload.supplier_id,
        article_id=payload.article_id,
        gross_quantity_kg=gross_qty,
        billing_quantity_kg=billing_qty,
        unit_price_eur_per_ton=payload.unit_price_eur_per_ton,
        gross_amount_eur=amounts["gross_amount"],
        total_deductions_eur=amounts["total_deductions"],
        net_amount_eur=amounts["net_amount"],
        currency="EUR",
        status="draft",
        note=payload.note,
        tenant_id=tenant_id,
    )
    db.add(settlement)
    db.flush()

    billing_qty_tons = amounts["billing_qty_tons"]
    for d in payload.deductions:
        deduction = AgrarSettlementDeduction(
            id=str(uuid.uuid4()),
            settlement_id=settlement.id,
            deduction_type=d.deduction_type,
            mode=d.mode,
            rate_per_ton_eur=d.rate_per_ton_eur,
            fixed_amount_eur=d.fixed_amount_eur,
            basis_quantity_tons=d.basis_quantity_tons if d.basis_quantity_tons is not None else billing_qty_tons,
            amount_eur=_calc_deduction_amount(d, billing_qty_tons),
            note=d.note,
            tenant_id=tenant_id,
        )
        db.add(deduction)

    db.commit()
    rows = db.query(AgrarSettlementDeduction).filter(AgrarSettlementDeduction.settlement_id == settlement.id).all()
    db.refresh(settlement)
    return _to_out(settlement, rows)


@router.get("/", response_model=list[SettlementOut])
async def list_settlements(
    status: Optional[SettlementStatus] = Query(None),
    supplier_id: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    query = db.query(AgrarSettlement).filter(AgrarSettlement.tenant_id == tenant_id)
    if status:
        query = query.filter(AgrarSettlement.status == status)
    if supplier_id:
        query = query.filter(AgrarSettlement.supplier_id == supplier_id)
    items = query.order_by(AgrarSettlement.created_at.desc()).limit(500).all()
    result: list[SettlementOut] = []
    for item in items:
        deductions = db.query(AgrarSettlementDeduction).filter(AgrarSettlementDeduction.settlement_id == item.id).all()
        result.append(_to_out(item, deductions))
    return result


@router.get("/{settlement_id}", response_model=SettlementOut)
async def get_settlement(
    settlement_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    settlement = db.query(AgrarSettlement).filter(AgrarSettlement.id == settlement_id, AgrarSettlement.tenant_id == tenant_id).first()
    if not settlement:
        raise HTTPException(status_code=404, detail="Settlement not found")
    deductions = db.query(AgrarSettlementDeduction).filter(AgrarSettlement.settlement_id == settlement.id).all()
    return _to_out(settlement, deductions)


@router.post("/{settlement_id}/post-fibu", response_model=dict)
async def post_settlement_to_fibu(
    settlement_id: str,
    payload: SettlementPostRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    settlement = db.query(AgrarSettlement).filter(AgrarSettlement.id == settlement_id, AgrarSettlement.tenant_id == tenant_id).first()
    if not settlement:
        raise HTTPException(status_code=404, detail="Settlement not found")
    if settlement.status != "draft":
        raise HTTPException(status_code=400, detail=f"Settlement cannot be posted in status {settlement.status}")

    posting_date = payload.posting_date or datetime.utcnow()
    journal_ref = f"JE-SET-{datetime.utcnow().strftime('%Y%m%d')}-{settlement.id[:8].upper()}"
    gross = _round_money(settlement.gross_amount_eur)
    deductions = _round_money(settlement.total_deductions_eur)
    net = _round_money(settlement.net_amount_eur)

    lines = [
        {
            "line_number": 1,
            "account_id": payload.debit_account,
            "debit_amount": float(gross),
            "credit_amount": 0.0,
            "description": f"Agrar settlement {settlement.settlement_number} gross",
        },
        {
            "line_number": 2,
            "account_id": payload.credit_account_supplier,
            "debit_amount": 0.0,
            "credit_amount": float(net),
            "description": f"Supplier payable {settlement.supplier_id}",
        },
    ]
    if deductions > 0:
        lines.append(
            {
                "line_number": 3,
                "account_id": payload.credit_account_deductions,
                "debit_amount": 0.0,
                "credit_amount": float(deductions),
                "description": "Settlement deductions",
            }
        )

    journal_entry = {
        "id": journal_ref,
        "tenant_id": tenant_id,
        "entry_number": journal_ref,
        "entry_date": posting_date.isoformat(),
        "posting_date": posting_date.isoformat(),
        "description": f"Agrar settlement {settlement.settlement_number}",
        "source": "agrar_settlement",
        "source_id": settlement.id,
        "status": "posted",
        "total_debit": float(gross),
        "total_credit": float(net + deductions),
        "lines": lines,
    }
    save_to_store("journal_entry", journal_ref, journal_entry, get_repository(db))

    settlement.status = "posted"
    settlement.posted_journal_ref = journal_ref
    settlement.posted_at = posting_date
    db.commit()
    return {"ok": True, "settlement_id": settlement.id, "journal_ref": journal_ref}


@router.post("/{settlement_id}/cancel", response_model=dict)
async def cancel_settlement(
    settlement_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    settlement = db.query(AgrarSettlement).filter(AgrarSettlement.id == settlement_id, AgrarSettlement.tenant_id == tenant_id).first()
    if not settlement:
        raise HTTPException(status_code=404, detail="Settlement not found")
    if settlement.status == "posted":
        raise HTTPException(status_code=400, detail="Posted settlement cannot be cancelled")
    settlement.status = "cancelled"
    db.commit()
    return {"ok": True, "settlement_id": settlement.id, "status": settlement.status}
