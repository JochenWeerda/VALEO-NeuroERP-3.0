"""
Agrar self-billing settlements with deduction and posting workflow (AGRAR-SET-01).
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from app.core.database import get_db
from app.core.data_quality_enforcement import (
    build_dq_error_detail,
    evaluate_settlement_datensatz,
)
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.tenant import get_tenant_id
from app.services.agrar_settlement_service import AgrarSettlementService
from app.services.agrar_drying_rule_service import DryingRuleService
from app.services.settlement_pdf_service import SettlementPdfService
from app.documents.router_helpers import get_repository, save_to_store
from app.infrastructure.models import AgrarSettlement, AgrarSettlementDeduction
from app.domains.inventory.api.inventory_auth import require_inventory_admin
from app.core.uuid7 import uuid7
from modules.agrar.services.moisture_engine import MoistureEngineInput, calculate_billing_weight
from modules.agrar.services.drying_rule_engine import (
    DryingFactorRange as _DryingFactorRange,
    DryingLookupRow as _DryingLookupRow,
    DryingRuleRepository as _DryingRuleRepository,
    DryingRuleSet as _DryingRuleSet,
    compute_settlement as _compute_drying_settlement,
)
from app.infrastructure.models import DryingRuleFactorRange, DryingRuleLookupRow, DryingRuleSet
from app.api.v1.endpoints.admin_core import _load_tenant_settings
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


def _build_settlement_dq_datensatz(payload: "SettlementCreate", settlement_number: str) -> dict:
    return {
        "abrechnungsnummer": settlement_number,
        "lieferant_id": payload.supplier_id,
        "brutto_gewicht_kg": payload.gross_quantity_kg,
        "abrechnungsgewicht_kg": payload.billing_quantity_kg if payload.billing_quantity_kg is not None else payload.gross_quantity_kg,
        "preis_eur_pro_t": payload.unit_price_eur_per_ton,
        "waehrung": "EUR",
    }


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


class DryingApplyInput(BaseModel):
    """
    Optional helper payload to compute invoice weight (Mengenabzug) + optional drying fee (€)
    from net weight + measured moisture using configured crop/site rules.

    Wichtig: keine doppelte Feuchte-Abzugslogik. Es wird ausschließlich die Methode
    des gefundenen Rule-Sets angewendet und als Audit-Snapshot persistiert.
    """

    crop_code: str = Field(..., min_length=2, max_length=40)
    site_id: Optional[str] = None
    moisture_pct: float = Field(..., ge=0, le=100)
    calc_date: Optional[str] = None  # defaults to today
    rounding_mode: Optional[str] = None  # ROUND_NEAREST|ROUND_UP|ROUND_DOWN


class SettlementCreate(BaseModel):
    settlement_number: Optional[str] = Field(default=None, min_length=3, max_length=50)
    campaign_id: Optional[str] = Field(default=None, min_length=1, max_length=64)
    contract_id: Optional[str] = None
    ticket_id: Optional[str] = None
    supplier_id: str
    article_id: Optional[str] = None
    gross_quantity_kg: float = Field(..., gt=0)
    billing_quantity_kg: Optional[float] = Field(default=None, gt=0)
    unit_price_eur_per_ton: float = Field(..., gt=0)
    deductions: list[DeductionInput] = Field(default_factory=list)
    note: Optional[str] = None
    drying: Optional[DryingApplyInput] = None


class SettlementPostRequest(BaseModel):
    debit_account: str = Field(default="5000", min_length=3, max_length=20)
    credit_account_supplier: str = Field(default="3300", min_length=3, max_length=20)
    credit_account_deductions: str = Field(default="5490", min_length=3, max_length=20)
    posting_date: Optional[datetime] = None
    expected_row_version: Optional[int] = Field(
        default=None,
        ge=1,
        description="Optimistic-Locking: zuletzt gelesene row_version der Abrechnung (optional, aber empfohlen).",
    )


class BillingWeightPreviewRequest(BaseModel):
    net_weight_kg: float = Field(..., gt=0)
    moisture_pct: float = Field(..., ge=0, lt=100)
    impurities_pct: float = Field(default=0.0, ge=0, lt=100)
    target_moisture_pct: float = Field(default=14.0, ge=0, lt=100)
    base_impurities_pct: float = Field(default=2.0, ge=0, lt=100)
    allow_bonus: bool = False


class DryingComputeRequest(BaseModel):
    crop_code: str = Field(..., min_length=2, max_length=40)
    site_id: Optional[str] = None
    net_weight_kg: float = Field(..., gt=0)
    moisture_pct: float = Field(..., ge=0, le=100)
    calc_date: Optional[str] = None  # YYYY-MM-DD, defaults to today
    rounding_mode: Optional[str] = None  # ROUND_NEAREST|ROUND_UP|ROUND_DOWN


class DryingComputeResponse(BaseModel):
    entzug_pct_points: float
    loss_pct: float
    loss_kg: float
    invoice_weight_kg: float
    drying_fee_eur: Optional[float] = None
    used_rule_set_id: str
    used_rule_version: int
    used_row_moisture_pct: Optional[float] = None
    warnings: list[str] = Field(default_factory=list)


class _DbDryingRuleRepo(_DryingRuleRepository):
    def __init__(self, db: Session, *, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    def find_rule_set(self, *, crop_code: str, site_id: Optional[str], calc_date, contract_id: Optional[str] = None, customer_id: Optional[str] = None) -> _DryingRuleSet:
        """
        Find rule set with priority:
        1. Customer-specific rule (if customer_id provided)
        2. Contract-specific rule (if contract_id provided)
        3. Site-specific rule
        4. Global rule (site_id=NULL)
        """
        def _base_q():
            return (
                self.db.query(DryingRuleSet)
                .filter(DryingRuleSet.tenant_id == self.tenant_id)
                .filter(DryingRuleSet.crop_code == crop_code)
                .filter(DryingRuleSet.is_active == True)  # noqa: E712
                .filter((DryingRuleSet.valid_from.is_(None)) | (DryingRuleSet.valid_from <= calc_date))
                .filter((DryingRuleSet.valid_to.is_(None)) | (DryingRuleSet.valid_to >= calc_date))
            )

        # 1. Customer-specific rule (höchste Priorität)
        if customer_id:
            row = (
                _base_q()
                .filter(DryingRuleSet.customer_id == customer_id)
                .filter(DryingRuleSet.is_customer_specific == True)  # noqa: E712
                .order_by(DryingRuleSet.valid_from.desc().nullslast(), DryingRuleSet.version.desc())
                .first()
            )
            if row:
                return self._row_to_rule_set(row)

        # 2. Contract-specific rule
        if contract_id:
            row = (
                _base_q()
                .filter(DryingRuleSet.contract_id == contract_id)
                .filter(DryingRuleSet.is_customer_specific == False)  # noqa: E712
                .order_by(DryingRuleSet.valid_from.desc().nullslast(), DryingRuleSet.version.desc())
                .first()
            )
            if row:
                return self._row_to_rule_set(row)

        # 3. Site-specific rule (nur allgemeingültige)
        row = None
        if site_id is not None:
            row = (
                _base_q()
                .filter(DryingRuleSet.site_id == site_id)
                .filter(DryingRuleSet.contract_id.is_(None))
                .filter(DryingRuleSet.is_customer_specific == False)  # noqa: E712
                .order_by(DryingRuleSet.valid_from.desc().nullslast(), DryingRuleSet.version.desc())
                .first()
            )
        # 4. Global rule (fallback)
        if row is None:
            row = (
                _base_q()
                .filter(DryingRuleSet.site_id.is_(None))
                .filter(DryingRuleSet.contract_id.is_(None))
                .filter(DryingRuleSet.is_customer_specific == False)  # noqa: E712
                .order_by(DryingRuleSet.valid_from.desc().nullslast(), DryingRuleSet.version.desc())
                .first()
            )
        if not row:
            raise HTTPException(status_code=404, detail=f"No drying rule set found for crop_code={crop_code} (site_id={site_id}, contract_id={contract_id}, customer_id={customer_id})")
        return self._row_to_rule_set(row)

    def _row_to_rule_set(self, row) -> _DryingRuleSet:
        return _DryingRuleSet(
            id=row.id,
            version=int(row.version),
            crop_code=row.crop_code,
            site_id=row.site_id,
            valid_from=row.valid_from,
            valid_to=row.valid_to,
            method=row.method,  # type: ignore[arg-type]
            base_moisture_pct=Decimal(str(row.base_moisture_pct)),
            rounding_mode=row.rounding_mode,  # type: ignore[arg-type]
            clamp_mode=row.clamp_mode,  # type: ignore[arg-type]
            min_moisture_pct=Decimal(str(row.min_moisture_pct)),
            max_moisture_pct=Decimal(str(row.max_moisture_pct)),
            start_threshold_moisture_pct=Decimal(str(row.start_threshold_moisture_pct)) if row.start_threshold_moisture_pct is not None else None,
            fee_basis=row.fee_basis,  # type: ignore[arg-type]
        )

    def list_lookup_rows(self, *, rule_set_id: str) -> list[_DryingLookupRow]:
        rows = (
            self.db.query(DryingRuleLookupRow)
            .filter(DryingRuleLookupRow.rule_set_id == rule_set_id)
            .order_by(DryingRuleLookupRow.moisture_pct.asc())
            .all()
        )
        return [
            _DryingLookupRow(
                moisture_pct=Decimal(str(r.moisture_pct)),
                entzug_pct_points=Decimal(str(r.entzug_pct_points)),
                loss_pct=Decimal(str(r.loss_pct)),
                fee_value=Decimal(str(r.fee_value)) if r.fee_value is not None else None,
                fee_unit=r.fee_unit,  # type: ignore[arg-type]
            )
            for r in rows
        ]

    def list_factor_ranges(self, *, rule_set_id: str) -> list[_DryingFactorRange]:
        rows = (
            self.db.query(DryingRuleFactorRange)
            .filter(DryingRuleFactorRange.rule_set_id == rule_set_id)
            .order_by(DryingRuleFactorRange.from_moisture_incl.asc())
            .all()
        )
        return [
            _DryingFactorRange(
                from_moisture_incl=Decimal(str(r.from_moisture_incl)),
                to_moisture_incl=Decimal(str(r.to_moisture_incl)),
                factor=Decimal(str(r.factor)),
            )
            for r in rows
        ]


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
    campaign_id: Optional[str] = None
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
    approval_status: str = "ENTWURF"
    approval_history: list[dict] = Field(default_factory=list)
    allowed_transitions: list[str] = Field(default_factory=list)
    can_post_fibu: bool = False
    correction_options: list[dict] = Field(default_factory=list)
    note: Optional[str] = None
    deductions: list[DeductionOut] = Field(default_factory=list)
    row_version: int = 1


class SettlementCampaignBackfillRequest(BaseModel):
    campaign_id: str = Field(..., min_length=1, max_length=64)
    dry_run: bool = False


class SettlementCampaignBackfillResponse(BaseModel):
    campaign_id: str
    matched_count: int
    updated_count: int
    ambiguous_count: int
    skipped_count: int
    updated_settlement_ids: list[str] = Field(default_factory=list)
    ambiguous_settlement_ids: list[str] = Field(default_factory=list)
    skipped_settlement_ids: list[str] = Field(default_factory=list)


def _current_settlement_row_version(settlement: AgrarSettlement) -> int:
    v = getattr(settlement, "row_version", None)
    return int(v) if v is not None else 1



def _get_settlement_approval_status(settlement: AgrarSettlement) -> str:
    drying_result = settlement.drying_result or {}
    return str(drying_result.get("approval_status") or "ENTWURF")


def _get_settlement_approval_history(settlement: AgrarSettlement) -> list[dict]:
    drying_result = settlement.drying_result or {}
    history = drying_result.get("approval_history") or []
    return list(history) if isinstance(history, list) else []


def _get_settlement_allowed_transitions(approval_status: str) -> list[str]:
    transition_map = {
        "ENTWURF": ["ZUR_FREIGABE", "ABGELEHNT"],
        "ZUR_FREIGABE": ["TEILWEISE_FREIGEGEBEN", "FREIGEGEBEN", "ABGELEHNT", "ENTWURF"],
        "TEILWEISE_FREIGEGEBEN": ["FREIGEGEBEN", "ABGELEHNT", "ZUR_FREIGABE"],
        "FREIGEGEBEN": ["VERBUCHT", "ABGELEHNT"],
        "ABGELEHNT": ["ENTWURF"],
        "VERBUCHT": [],
    }
    return transition_map.get(approval_status, [])


def _build_settlement_correction_options(settlement: AgrarSettlement, approval_status: str) -> list[dict]:
    if settlement.status != "posted":
        return []
    base_note = f"Settlement {settlement.settlement_number} / Journal {settlement.posted_journal_ref or '-'}"
    return [
        {
            "memo_type": "credit",
            "label": "Gutschrift erstellen",
            "reason": f"Gutschrift zur Settlement-Korrektur ({base_note})",
        },
        {
            "memo_type": "debit",
            "label": "Belastung erstellen",
            "reason": f"Belastung zur Settlement-Korrektur ({base_note})",
        },
        {
            "memo_type": "rework",
            "label": "Korrektur ueber Belegpfad dokumentieren",
            "reason": f"Settlement ist bereits verbucht; Korrektur nur ueber Gutschrift/Belastung ({base_note})",
        },
    ]


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
    approval_status = _get_settlement_approval_status(settlement)
    return SettlementOut(
        id=settlement.id,
        settlement_number=settlement.settlement_number,
        campaign_id=getattr(settlement, "campaign_id", None),
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
        approval_status=approval_status,
        approval_history=_get_settlement_approval_history(settlement),
        allowed_transitions=_get_settlement_allowed_transitions(approval_status),
        can_post_fibu=settlement.status == "draft" and approval_status == "FREIGEGEBEN",
        correction_options=_build_settlement_correction_options(settlement, approval_status),
        note=settlement.note,
        row_version=_current_settlement_row_version(settlement),
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


def _parse_campaign_window(campaign: dict[str, Any]) -> tuple[date, date] | None:
    try:
        return (
            date.fromisoformat(str(campaign.get("start_date"))),
            date.fromisoformat(str(campaign.get("end_date"))),
        )
    except Exception:
        return None


def _to_created_date(value: object) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except ValueError:
            return None
    return None


def _build_campaign_backfill_plan(
    *,
    campaign_id: str,
    campaigns: list[dict[str, Any]],
    settlements: list[AgrarSettlement],
) -> SettlementCampaignBackfillResponse:
    target_campaign = next((campaign for campaign in campaigns if str(campaign.get("id")) == campaign_id), None)
    if target_campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    target_window = _parse_campaign_window(target_campaign)
    if target_window is None:
        raise HTTPException(status_code=409, detail="Campaign date range is invalid")

    updated_ids: list[str] = []
    ambiguous_ids: list[str] = []
    skipped_ids: list[str] = []
    start_date, end_date = target_window

    valid_campaigns = [(campaign, _parse_campaign_window(campaign)) for campaign in campaigns]
    valid_campaigns = [(campaign, window) for campaign, window in valid_campaigns if window is not None]

    for settlement in settlements:
        if getattr(settlement, "campaign_id", None):
            continue
        created_on = _to_created_date(getattr(settlement, "created_at", None))
        if created_on is None:
            skipped_ids.append(str(settlement.id))
            continue
        if created_on < start_date or created_on > end_date:
            continue

        matching_campaign_ids = [
            str(campaign.get("id"))
            for campaign, window in valid_campaigns
            if window[0] <= created_on <= window[1]
        ]
        if campaign_id not in matching_campaign_ids:
            continue
        if len(matching_campaign_ids) > 1:
            ambiguous_ids.append(str(settlement.id))
            continue
        updated_ids.append(str(settlement.id))

    return SettlementCampaignBackfillResponse(
        campaign_id=campaign_id,
        matched_count=len(updated_ids) + len(ambiguous_ids) + len(skipped_ids),
        updated_count=len(updated_ids),
        ambiguous_count=len(ambiguous_ids),
        skipped_count=len(skipped_ids),
        updated_settlement_ids=updated_ids,
        ambiguous_settlement_ids=ambiguous_ids,
        skipped_settlement_ids=skipped_ids,
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


@router.post("/drying/compute", response_model=DryingComputeResponse)
async def compute_drying_settlement(
    payload: DryingComputeRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    calc_date = payload.calc_date or datetime.utcnow().date().isoformat()
    repo = _DbDryingRuleRepo(db, tenant_id=tenant_id)
    try:
        result = _compute_drying_settlement(
            repo,
            {
                "cropCode": payload.crop_code,
                "siteId": payload.site_id,
                "netWeightKg": payload.net_weight_kg,
                "moisturePct": payload.moisture_pct,
                "calcDate": calc_date,
                "roundingMode": payload.rounding_mode,
                "contractId": payload.contract_id,
                "customerId": payload.customer_id,
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return DryingComputeResponse(
        entzug_pct_points=float(result.entzug_pct_points),
        loss_pct=float(result.loss_pct),
        loss_kg=float(result.loss_kg),
        invoice_weight_kg=float(result.invoice_weight_kg),
        drying_fee_eur=float(result.drying_fee_eur) if result.drying_fee_eur is not None else None,
        used_rule_set_id=result.used_rule_set_id,
        used_rule_version=int(result.used_rule_version),
        used_row_moisture_pct=float(result.used_row_moisture_pct) if result.used_row_moisture_pct is not None else None,
        warnings=list(result.warnings),
    )


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
    try:
        settlement, rows = _svc(db, tenant_id).create_settlement_with_drying(
            payload,
            drying_compute_fn=_compute_drying_settlement,
            drying_repo=_DbDryingRuleRepo(db, tenant_id=tenant_id),
        )
    except ValidationFailedError as exc:
        raise HTTPException(status_code=422, detail=exc.detail)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.detail)
    return _to_out(settlement, rows)


def _svc(db: Session, tenant_id: str) -> AgrarSettlementService:
    return AgrarSettlementService(db, tenant_id)


def _drying_svc(db: Session, tenant_id: str) -> DryingRuleService:
    return DryingRuleService(db, tenant_id)


@router.get("/", response_model=list[SettlementOut])
async def list_settlements(
    status: Optional[SettlementStatus] = Query(None),
    supplier_id: Optional[str] = Query(None),
    campaign_id: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    pairs = _svc(db, tenant_id).list_settlements(
        status=status, supplier_id=supplier_id, campaign_id=campaign_id
    )
    return [_to_out(s, d) for s, d in pairs]


@router.post("/campaign-reference/backfill", response_model=SettlementCampaignBackfillResponse)
async def backfill_settlement_campaign_reference(
    payload: SettlementCampaignBackfillRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    settings = _load_tenant_settings(db, tenant_id)
    campaigns = settings.get("erntefenster_campaigns")
    campaign_list = [campaign for campaign in campaigns if isinstance(campaign, dict)] if isinstance(campaigns, list) else []

    settlements = (
        db.query(AgrarSettlement)
        .filter(AgrarSettlement.tenant_id == tenant_id)
        .filter(AgrarSettlement.campaign_id.is_(None))
        .all()
    )
    plan = _build_campaign_backfill_plan(
        campaign_id=payload.campaign_id,
        campaigns=campaign_list,
        settlements=settlements,
    )

    if payload.dry_run or plan.updated_count == 0:
        return plan

    updatable_ids = set(plan.updated_settlement_ids)
    for settlement in settlements:
        if str(settlement.id) in updatable_ids:
            settlement.campaign_id = payload.campaign_id
    try:
        db.commit()
    except StaleDataError:
        db.rollback()
        raise HTTPException(status_code=409, detail={"code": "row_version_conflict", "message": "Abrechnung wurde zwischenzeitlich geändert."})
    return plan


@router.get("/{settlement_id}", response_model=SettlementOut)
async def get_settlement(
    settlement_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        settlement, deductions = _svc(db, tenant_id).get_settlement(settlement_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    return _to_out(settlement, deductions)


@router.post("/{settlement_id}/post-fibu", response_model=dict)
async def post_settlement_to_fibu(
    settlement_id: str,
    payload: SettlementPostRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        return _svc(db, tenant_id).post_to_fibu_full(settlement_id, payload)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.detail)
    except ValidationFailedError as exc:
        raise HTTPException(status_code=400, detail=exc.detail)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"FIBU-Buchung fehlgeschlagen: {exc}") from exc


class SettlementCorrectionDraftOut(BaseModel):
    settlement_id: str
    settlement_number: str
    memo_type: Literal["credit", "debit"]
    supplier_id: str
    supplier_name: Optional[str] = None
    posted_journal_ref: Optional[str] = None
    suggested_reason: str
    suggested_notes: str
    suggested_route: str
    items: list[dict] = Field(default_factory=list)


class SettlementCompletionStatusOut(BaseModel):
    settlement_id: str
    variant: Literal["GUTSCHRIFT", "BELASTUNG", "KORREKTUR"]
    completed: bool
    completion_pct: int
    missing_controls: list[str] = Field(default_factory=list)
    next_step: Optional[str] = None
    linked_documents: list[dict] = Field(default_factory=list)


@router.get("/{settlement_id}/correction-draft", response_model=SettlementCorrectionDraftOut)
async def get_settlement_correction_draft(
    settlement_id: str,
    memo_type: Literal["credit", "debit"] = Query(...),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        data = _svc(db, tenant_id).get_correction_draft(settlement_id, memo_type)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.detail)
    return SettlementCorrectionDraftOut(**data)


@router.get("/{settlement_id}/completion-status", response_model=SettlementCompletionStatusOut)
async def get_settlement_completion_status(
    settlement_id: str,
    variant: Literal["GUTSCHRIFT", "BELASTUNG", "KORREKTUR"] = Query(...),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        data = _svc(db, tenant_id).get_completion_status(settlement_id, variant)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return SettlementCompletionStatusOut(**data)


@router.post("/{settlement_id}/cancel", response_model=dict)
async def cancel_settlement(
    settlement_id: str,
    expected_row_version: Optional[int] = Query(
        default=None,
        ge=1,
        description="Optimistic-Locking: zuletzt gelesene row_version (optional).",
    ),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        settlement, _ = _svc(db, tenant_id).get_settlement(settlement_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    try:
        _svc(db, tenant_id).check_row_version(settlement, expected_row_version)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.detail)
    try:
        result = _svc(db, tenant_id).cancel_settlement(settlement_id)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.detail)
    except ValidationFailedError as exc:
        raise HTTPException(status_code=400, detail=exc.detail)
    return {"ok": True, "settlement_id": result.id, "status": result.status}


# ── Drying Rule Sets CRUD (Admin-only write, read for all) ──────────────────────

def _get_user_id_from_request(request: Request) -> Optional[str]:
    """Extract user ID from request state (token claims)."""
    claims = getattr(request.state, 'token_claims', {})
    return claims.get('sub') or claims.get('user_id')


class DryingRuleSetCreate(BaseModel):
    crop_code: str = Field(..., min_length=1, max_length=40)
    site_id: Optional[str] = Field(None, max_length=64)
    valid_from: Optional[str] = Field(None, description="ISO date (YYYY-MM-DD)")
    valid_to: Optional[str] = Field(None, description="ISO date (YYYY-MM-DD)")
    method: Literal["LOOKUP_TABLE", "FACTOR_FROM_BASE", "DRY_MATTER_NORMALIZATION"] = Field(...)
    base_moisture_pct: float = Field(..., ge=0, le=100)
    rounding_mode: Literal["ROUND_NEAREST", "ROUND_UP", "ROUND_DOWN"] = Field(default="ROUND_NEAREST")
    clamp_mode: Literal["CLAMP_TO_MAX", "HARD_ERROR"] = Field(default="HARD_ERROR")
    min_moisture_pct: float = Field(default=0, ge=0, le=100)
    max_moisture_pct: float = Field(default=60, ge=0, le=100)
    start_threshold_moisture_pct: Optional[float] = Field(None, ge=0, le=100)
    fee_basis: Literal["INVOICE_WEIGHT", "NET_WEIGHT"] = Field(default="INVOICE_WEIGHT")
    contract_id: Optional[str] = Field(None, description="Verknüpfung zu Ankaufskontrakt (optional)")
    customer_id: Optional[str] = Field(None, description="Kunde für Sonderregelung (optional)")
    is_customer_specific: bool = Field(default=False)
    justification: Optional[str] = Field(None, description="Begründung für kundenspezifische Sonderregelungen (erforderlich wenn is_customer_specific=True)")
    document_id: Optional[str] = Field(None, max_length=64, description="DMS-Referenz für Tabelle/Formel-Dokument")

    @model_validator(mode="after")
    def validate_customer_specific(self):
        if self.is_customer_specific and not self.customer_id:
            raise ValueError("customer_id is required when is_customer_specific=True")
        if self.is_customer_specific and not self.justification:
            raise ValueError("justification is required when is_customer_specific=True")
        return self


class DryingRuleSetUpdate(BaseModel):
    site_id: Optional[str] = Field(None, max_length=64)
    valid_from: Optional[str] = Field(None, description="ISO date (YYYY-MM-DD)")
    valid_to: Optional[str] = Field(None, description="ISO date (YYYY-MM-DD)")
    method: Optional[Literal["LOOKUP_TABLE", "FACTOR_FROM_BASE", "DRY_MATTER_NORMALIZATION"]] = None
    base_moisture_pct: Optional[float] = Field(None, ge=0, le=100)
    rounding_mode: Optional[Literal["ROUND_NEAREST", "ROUND_UP", "ROUND_DOWN"]] = None
    clamp_mode: Optional[Literal["CLAMP_TO_MAX", "HARD_ERROR"]] = None
    min_moisture_pct: Optional[float] = Field(None, ge=0, le=100)
    max_moisture_pct: Optional[float] = Field(None, ge=0, le=100)
    start_threshold_moisture_pct: Optional[float] = Field(None, ge=0, le=100)
    fee_basis: Optional[Literal["INVOICE_WEIGHT", "NET_WEIGHT"]] = None
    contract_id: Optional[str] = None
    customer_id: Optional[str] = None
    is_customer_specific: Optional[bool] = None
    justification: Optional[str] = None
    document_id: Optional[str] = Field(None, max_length=64)
    is_active: Optional[bool] = None

    @model_validator(mode="after")
    def validate_customer_specific(self):
        if self.is_customer_specific is True and not self.customer_id:
            raise ValueError("customer_id is required when is_customer_specific=True")
        if self.is_customer_specific is True and not self.justification:
            raise ValueError("justification is required when is_customer_specific=True")
        return self


class DryingRuleSetOut(BaseModel):
    id: str
    crop_code: str
    site_id: Optional[str]
    valid_from: Optional[str]
    valid_to: Optional[str]
    version: int
    is_active: bool
    method: str
    base_moisture_pct: float
    rounding_mode: str
    clamp_mode: str
    min_moisture_pct: float
    max_moisture_pct: float
    start_threshold_moisture_pct: Optional[float]
    fee_basis: str
    created_at: str
    created_by: Optional[str]
    updated_at: Optional[str]
    updated_by: Optional[str]
    contract_id: Optional[str]
    customer_id: Optional[str]
    is_customer_specific: bool
    justification: Optional[str]
    document_id: Optional[str]


def _to_drying_rule_out(r: DryingRuleSet) -> DryingRuleSetOut:
    return DryingRuleSetOut(
        id=r.id,
        crop_code=r.crop_code,
        site_id=r.site_id,
        valid_from=r.valid_from.isoformat() if r.valid_from else None,
        valid_to=r.valid_to.isoformat() if r.valid_to else None,
        version=int(r.version),
        is_active=r.is_active,
        method=r.method,
        base_moisture_pct=float(r.base_moisture_pct),
        rounding_mode=r.rounding_mode,
        clamp_mode=r.clamp_mode,
        min_moisture_pct=float(r.min_moisture_pct),
        max_moisture_pct=float(r.max_moisture_pct),
        start_threshold_moisture_pct=float(r.start_threshold_moisture_pct) if r.start_threshold_moisture_pct else None,
        fee_basis=r.fee_basis,
        created_at=r.created_at.isoformat() if r.created_at else "",
        created_by=r.created_by,
        updated_at=r.updated_at.isoformat() if r.updated_at else None,
        updated_by=r.updated_by,
        contract_id=r.contract_id,
        customer_id=r.customer_id,
        is_customer_specific=r.is_customer_specific,
        justification=r.justification,
        document_id=r.document_id,
    )


def _to_lookup_row_out(r: DryingRuleLookupRow) -> DryingLookupRowOut:
    return DryingLookupRowOut(
        id=r.id,
        rule_set_id=r.rule_set_id,
        moisture_pct=float(r.moisture_pct),
        entzug_pct_points=float(r.entzug_pct_points),
        loss_pct=float(r.loss_pct),
        fee_value=float(r.fee_value) if r.fee_value is not None else None,
        fee_unit=r.fee_unit,
        created_at=r.created_at.isoformat() if r.created_at else "",
    )


def _to_factor_range_out(r: DryingRuleFactorRange) -> DryingFactorRangeOut:
    return DryingFactorRangeOut(
        id=r.id,
        rule_set_id=r.rule_set_id,
        from_moisture_incl=float(r.from_moisture_incl),
        to_moisture_incl=float(r.to_moisture_incl),
        factor=float(r.factor),
        created_at=r.created_at.isoformat() if r.created_at else "",
    )


@router.get("/drying-rules", response_model=list[DryingRuleSetOut])
async def list_drying_rules(
    crop_code: Optional[str] = Query(None),
    contract_id: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    is_customer_specific: Optional[bool] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Liste aller Trocknungs-/Schwundtabellen (Leserechte für alle)."""
    rules = _drying_svc(db, tenant_id).list_rules(
        crop_code=crop_code, contract_id=contract_id,
        customer_id=customer_id, is_customer_specific=is_customer_specific,
    )
    return [_to_drying_rule_out(r) for r in rules]


@router.get("/drying-rules/{rule_id}", response_model=DryingRuleSetOut)
async def get_drying_rule(
    rule_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Einzelne Trocknungs-/Schwundtabelle abrufen (Leserechte für alle)."""
    try:
        rule = _drying_svc(db, tenant_id).get_rule(rule_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    return _to_drying_rule_out(rule)


@router.post("/drying-rules", response_model=DryingRuleSetOut, status_code=201)
async def create_drying_rule(
    payload: DryingRuleSetCreate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),  # Nur Admin kann schreiben
):
    """Neue Trocknungs-/Schwundtabelle anlegen (nur Admin)."""
    user_id = _get_user_id_from_request(request) or "system"
    rule = _drying_svc(db, tenant_id).create_rule(payload, user_id)
    return _to_drying_rule_out(rule)


@router.put("/drying-rules/{rule_id}", response_model=DryingRuleSetOut)
async def update_drying_rule(
    rule_id: str,
    payload: DryingRuleSetUpdate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),  # Nur Admin kann schreiben
):
    """Trocknungs-/Schwundtabelle aktualisieren (nur Admin). Erstellt neue Version bei Änderungen."""
    user_id = _get_user_id_from_request(request) or "system"
    try:
        rule = _drying_svc(db, tenant_id).update_rule(rule_id, payload, user_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    return _to_drying_rule_out(rule)


@router.delete("/drying-rules/{rule_id}", status_code=204)
async def delete_drying_rule(
    rule_id: str,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),  # Nur Admin kann löschen
):
    """Trocknungs-/Schwundtabelle löschen (nur Admin). Soft-Delete: is_active=False."""
    user_id = _get_user_id_from_request(request) or "system"
    try:
        _drying_svc(db, tenant_id).delete_rule(rule_id, user_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)


@router.get("/drying-rules/{rule_id}/download", response_model=dict)
async def download_drying_rule_document(
    rule_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Portal-Download für Trocknungs-/Schwundtabelle (für Kunden).
    Gibt DMS-Referenz oder Regel-Daten als JSON zurück (später: PDF-Export).
    """
    try:
        return _drying_svc(db, tenant_id).get_rule_download_data(rule_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)


# ── Drying Rule Lookup Rows CRUD (Admin-only) ────────────────────────────────

class DryingLookupRowCreate(BaseModel):
    rule_set_id: str
    moisture_pct: float = Field(..., ge=0, le=100, description="Feuchte in % (0.1-Schritte)")
    entzug_pct_points: float = Field(..., ge=0, description="Entzug in %-Punkten")
    loss_pct: float = Field(..., ge=0, le=100, description="Schwund in %")
    fee_value: Optional[float] = Field(None, ge=0, description="Trocknungskosten (optional)")
    fee_unit: Optional[Literal["EUR_PER_T", "EUR_PER_DT", "EUR_FIXED"]] = Field(None, description="Einheit der Trocknungskosten")


class DryingLookupRowUpdate(BaseModel):
    moisture_pct: Optional[float] = Field(None, ge=0, le=100)
    entzug_pct_points: Optional[float] = Field(None, ge=0)
    loss_pct: Optional[float] = Field(None, ge=0, le=100)
    fee_value: Optional[float] = Field(None, ge=0)
    fee_unit: Optional[Literal["EUR_PER_T", "EUR_PER_DT", "EUR_FIXED"]] = None


class DryingLookupRowOut(BaseModel):
    id: str
    rule_set_id: str
    moisture_pct: float
    entzug_pct_points: float
    loss_pct: float
    fee_value: Optional[float]
    fee_unit: Optional[str]
    created_at: str


@router.get("/drying-rules/{rule_id}/lookup-rows", response_model=list[DryingLookupRowOut])
async def list_drying_lookup_rows(
    rule_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Lookup-Rows einer Regel auflisten (Leserechte für alle)."""
    try:
        rows = _drying_svc(db, tenant_id).list_lookup_rows(rule_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    return [_to_lookup_row_out(r) for r in rows]


@router.post("/drying-rules/lookup-rows", response_model=DryingLookupRowOut, status_code=201)
async def create_drying_lookup_row(
    payload: DryingLookupRowCreate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),  # Nur Admin kann schreiben
):
    """Lookup-Row anlegen (nur Admin)."""
    try:
        row = _drying_svc(db, tenant_id).create_lookup_row(payload)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except ValidationFailedError as exc:
        raise HTTPException(status_code=400, detail=exc.detail)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.detail)
    return _to_lookup_row_out(row)


@router.put("/drying-rules/lookup-rows/{row_id}", response_model=DryingLookupRowOut)
async def update_drying_lookup_row(
    row_id: str,
    payload: DryingLookupRowUpdate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),  # Nur Admin kann schreiben
):
    """Lookup-Row aktualisieren (nur Admin)."""
    try:
        row = _drying_svc(db, tenant_id).update_lookup_row(row_id, payload)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.detail)
    return _to_lookup_row_out(row)


@router.delete("/drying-rules/lookup-rows/{row_id}", status_code=204)
async def delete_drying_lookup_row(
    row_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),  # Nur Admin kann löschen
):
    """Lookup-Row löschen (nur Admin)."""
    try:
        _drying_svc(db, tenant_id).delete_lookup_row(row_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)


# ── Drying Rule Factor Ranges CRUD (Admin-only) ───────────────────────────────

class DryingFactorRangeCreate(BaseModel):
    rule_set_id: str
    from_moisture_incl: float = Field(..., ge=0, le=100, description="Von Feuchte in % (inklusive, 0.1-Schritte)")
    to_moisture_incl: float = Field(..., ge=0, le=100, description="Bis Feuchte in % (inklusive, 0.1-Schritte)")
    factor: float = Field(..., gt=0, description="Faktor für Schwundberechnung")

    @model_validator(mode="after")
    def validate_range(self):
        if self.from_moisture_incl > self.to_moisture_incl:
            raise ValueError("from_moisture_incl must be <= to_moisture_incl")
        return self


class DryingFactorRangeUpdate(BaseModel):
    from_moisture_incl: Optional[float] = Field(None, ge=0, le=100)
    to_moisture_incl: Optional[float] = Field(None, ge=0, le=100)
    factor: Optional[float] = Field(None, gt=0)

    @model_validator(mode="after")
    def validate_range(self):
        if self.from_moisture_incl is not None and self.to_moisture_incl is not None:
            if self.from_moisture_incl > self.to_moisture_incl:
                raise ValueError("from_moisture_incl must be <= to_moisture_incl")
        return self


class DryingFactorRangeOut(BaseModel):
    id: str
    rule_set_id: str
    from_moisture_incl: float
    to_moisture_incl: float
    factor: float
    created_at: str


@router.get("/drying-rules/{rule_id}/factor-ranges", response_model=list[DryingFactorRangeOut])
async def list_drying_factor_ranges(
    rule_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Factor-Ranges einer Regel auflisten (Leserechte für alle)."""
    try:
        ranges = _drying_svc(db, tenant_id).list_factor_ranges(rule_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    return [_to_factor_range_out(r) for r in ranges]


@router.post("/drying-rules/factor-ranges", response_model=DryingFactorRangeOut, status_code=201)
async def create_drying_factor_range(
    payload: DryingFactorRangeCreate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),  # Nur Admin kann schreiben
):
    """Factor-Range anlegen (nur Admin)."""
    try:
        range_obj = _drying_svc(db, tenant_id).create_factor_range(payload)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except ValidationFailedError as exc:
        raise HTTPException(status_code=400, detail=exc.detail)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.detail)
    return _to_factor_range_out(range_obj)


@router.put("/drying-rules/factor-ranges/{range_id}", response_model=DryingFactorRangeOut)
async def update_drying_factor_range(
    range_id: str,
    payload: DryingFactorRangeUpdate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),  # Nur Admin kann schreiben
):
    """Factor-Range aktualisieren (nur Admin)."""
    try:
        range_obj = _drying_svc(db, tenant_id).update_factor_range(range_id, payload)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.detail)
    return _to_factor_range_out(range_obj)


@router.delete("/drying-rules/factor-ranges/{range_id}", status_code=204)
async def delete_drying_factor_range(
    range_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    _: str = Depends(require_inventory_admin),  # Nur Admin kann löschen
):
    """Factor-Range löschen (nur Admin)."""
    try:
        _drying_svc(db, tenant_id).delete_factor_range(range_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)


# ============================================================================
# PDF-EXPORT FÜR ABRECHNUNGEN
# ============================================================================

@router.get("/{settlement_id}/export-pdf")
async def export_settlement_pdf(
    settlement_id: str,
    archive: bool = False,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Exportiere Abrechnung als PDF (GoBD-konform).

    Query-Parameter:
    - archive=true  → PDF zusätzlich in GoBD-Artifact-Store registrieren
    """
    from fastapi.responses import Response as FastAPIResponse
    from app.infrastructure.models import Article
    from app.infrastructure.models.business_partner import BusinessPartner

    try:
        settlement, deductions = _svc(db, tenant_id).get_settlement(settlement_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)

    supplier = db.query(BusinessPartner).filter(
        BusinessPartner.id == settlement.supplier_id,
        BusinessPartner.tenant_id == tenant_id,
    ).first()
    article = None
    if settlement.article_id:
        article = db.query(Article).filter(Article.id == settlement.article_id).first()

    pdf_svc = SettlementPdfService(db, tenant_id)

    if archive:
        meta = pdf_svc.generate_and_archive(settlement, deductions, supplier, article)
        pdf_bytes = meta.pop("pdf_bytes")
    else:
        pdf_bytes = pdf_svc.generate_bytes(settlement, deductions, supplier, article)

    filename = f"abrechnung_{settlement.settlement_number or settlement.id}.pdf"
    return FastAPIResponse(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ============================================================================
# GAP 003 — Trocknungsabrechnung Core-Contract API (Wave 72)
# Exponiert compute_trocknungs_abrechnung() mit SHA-256 Audit-Hash
# ============================================================================

from app.core.trocknungs_abrechnung import (
    TrocknungsInput,
    TrocknungsMethode,
    TrocknungsRegelParametrierung,
    compute_trocknungs_abrechnung,
    validate_trocknungs_ergebnis,
    get_default_trocknungsregeln,
)


class TrocknungsAbrechnungPreviewRequest(BaseModel):
    """Stateless Preview: Trocknungsabrechnung mit SHA-256 Audit-Hash berechnen."""
    crop_code: str = Field(..., min_length=2, max_length=10, description="Fruchtartcode (WW, SG, RA, KM, ZR, ...)")
    brutto_gewicht_kg: float = Field(..., gt=0, description="Bruttoeingangsgewicht in kg")
    eingangs_feuchte_pct: float = Field(..., ge=0, le=100, description="Gemessene Feuchte bei Annahme in %")
    ziel_feuchte_pct: float = Field(..., ge=0, le=100, description="Vertraglich vereinbarte Zielfeuchte in %")
    methode: str = Field(default="FAKTOR_STUFUNG", description="Berechnungsmethode")
    rule_set_id: str = Field(default="default", description="Regelwerk-Referenz (für Audit-Hash)")
    rule_set_version: int = Field(default=1, ge=1, description="Regelwerk-Version")
    settlement_id: str = Field(default="preview", description="Settlement-ID (für Audit-Hash)")
    tenant_id: str = Field(default="system", description="Mandant")
    # Optionale Überschreibung der Berechnungsparameter (sonst Branchenrichtwerte)
    start_threshold_pct: Optional[float] = Field(default=None, ge=0, le=100)
    trocknungskosten_eur_per_pct_per_t: Optional[float] = Field(default=None, ge=0)
    schwund_faktor: Optional[float] = Field(default=None, gt=0)
    max_abzug_pct: Optional[float] = Field(default=None, ge=0, le=100)


@router.post("/trocknungs-abrechnung/preview", response_model=dict, tags=["agrar", "trocknung"])
async def preview_trocknungs_abrechnung(payload: TrocknungsAbrechnungPreviewRequest):
    """
    Trocknungsabrechnung preview mit GoBD-konformem SHA-256 Audit-Hash.

    Verwendet compute_trocknungs_abrechnung() aus dem Core-Contract (Wave 26/Gap 003).
    Liefert alle Abzugspositionen, Nettogewicht und deterministischen Audit-Hash.
    Kein DB-Aufruf — rein deterministisch.
    """
    try:
        methode = TrocknungsMethode(payload.methode)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Unbekannte Methode: {payload.methode}. Erlaubt: {[m.value for m in TrocknungsMethode]}")

    inp = TrocknungsInput(
        settlement_id=payload.settlement_id,
        tenant_id=payload.tenant_id,
        crop_code=payload.crop_code,
        rule_set_id=payload.rule_set_id,
        rule_set_version=payload.rule_set_version,
        brutto_gewicht_kg=Decimal(str(payload.brutto_gewicht_kg)),
        eingangs_feuchte_pct=Decimal(str(payload.eingangs_feuchte_pct)),
        ziel_feuchte_pct=Decimal(str(payload.ziel_feuchte_pct)),
        methode=methode,
    )

    # Parameter: explizit aus Request oder Branchenrichtwerte je Fruchtart
    defaults = get_default_trocknungsregeln()
    default_params = defaults.get(payload.crop_code.upper(), TrocknungsRegelParametrierung())
    params = TrocknungsRegelParametrierung(
        start_threshold_pct=Decimal(str(payload.start_threshold_pct)) if payload.start_threshold_pct is not None else default_params.start_threshold_pct,
        trocknungskosten_eur_per_pct_per_t=Decimal(str(payload.trocknungskosten_eur_per_pct_per_t)) if payload.trocknungskosten_eur_per_pct_per_t is not None else default_params.trocknungskosten_eur_per_pct_per_t,
        schwund_faktor=Decimal(str(payload.schwund_faktor)) if payload.schwund_faktor is not None else default_params.schwund_faktor,
        max_abzug_pct=Decimal(str(payload.max_abzug_pct)) if payload.max_abzug_pct is not None else default_params.max_abzug_pct,
    )

    ergebnis = compute_trocknungs_abrechnung(inp, params)
    validierung = validate_trocknungs_ergebnis(ergebnis)
    return {**ergebnis.as_dict(), "validierung": validierung.as_dict()}


@router.get("/trocknungs-regelsets/defaults", response_model=dict, tags=["agrar", "trocknung"])
async def get_trocknungs_regelsets_defaults():
    """
    Branchenrichtwerte für Trocknungsparameter je Fruchtart zurückgeben.

    Basis: DLG-Empfehlungen, UFOP-Richtwerte, Handelsusancen 2024.
    Tenants können eigene Regelsets in der DB konfigurieren (GET /drying-rules).
    """
    defaults = get_default_trocknungsregeln()
    return {
        "schema_version": 1,
        "quelle": "DLG-Empfehlungen / UFOP-Richtwerte / Handelsusancen 2024",
        "regelsets": {
            crop_code: {
                "crop_code": crop_code,
                "start_threshold_pct": float(params.start_threshold_pct),
                "trocknungskosten_eur_per_pct_per_t": float(params.trocknungskosten_eur_per_pct_per_t),
                "schwund_faktor": float(params.schwund_faktor),
                "max_abzug_pct": float(params.max_abzug_pct) if params.max_abzug_pct is not None else None,
            }
            for crop_code, params in defaults.items()
        },
    }


# ============================================================================
# GAP 004 — Settlement Freigabe-Flow + Gutschrift/Belastung (Wave 73)
# Exponiert evaluate_settlement_approval() via REST
# ============================================================================

from app.core.settlement_approval import (
    SettlementApprovalRequest,
    SettlementApprovalStatus,
    SettlementActorType,
    evaluate_settlement_approval,
    get_allowed_transitions,
    is_terminal,
)


class SettlementFreigabeRequest(BaseModel):
    """Freigabe-Anfrage: Status-Übergang mit Aktor-Kontext."""
    actor_id: str = Field(..., min_length=1, description="Benutzer- oder System-ID")
    actor_type: str = Field(..., description="Aktor-Typ: SACHBEARBEITER, ABTEILUNGSLEITER, PROKURIST, AGENT, SYSTEM")
    target_status: str = Field(..., description="Ziel-Status: ZUR_FREIGABE, FREIGEGEBEN, ABGELEHNT, VERBUCHT, ...")
    reason: Optional[str] = Field(default=None, description="Begründung (optional)")
    current_status: Optional[str] = Field(default=None, description="Aktueller Status (für stateless Evaluation; leer = aus DB)")
    expected_row_version: Optional[int] = Field(
        default=None,
        ge=1,
        description="Optimistic-Locking: zuletzt gelesene row_version der Abrechnung (optional).",
    )


@router.post("/freigabe/evaluate", response_model=dict, tags=["agrar", "settlement", "freigabe"])
async def evaluate_settlement_freigabe_stateless(payload: SettlementFreigabeRequest):
    """
    Stateless Freigabe-Evaluation: Prüft ob ein Status-Übergang zulässig ist.

    Kein DB-Zugriff — für Previews, Tests und Agent-Checks.
    Gibt allowed=True/False + Audit-Entry zurück.
    """
    try:
        actor_type = SettlementActorType(payload.actor_type)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Unbekannter actor_type: {payload.actor_type}")

    try:
        target_status = SettlementApprovalStatus(payload.target_status)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Unbekannter target_status: {payload.target_status}")

    current_status_str = payload.current_status or "ENTWURF"
    try:
        current_status = SettlementApprovalStatus(current_status_str)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Unbekannter current_status: {current_status_str}")

    request = SettlementApprovalRequest(
        settlement_id="preview",
        tenant_id="system",
        actor_id=payload.actor_id,
        actor_type=actor_type,
        target_status=target_status,
        reason=payload.reason,
    )
    result = evaluate_settlement_approval(request, current_status)
    return {
        **result.audit_entry,
        "allowed_transitions": [s.value for s in get_allowed_transitions(current_status)],
        "is_terminal": is_terminal(current_status),
    }


@router.post("/{settlement_id}/freigabe", response_model=dict, tags=["agrar", "settlement", "freigabe"])
async def settlement_freigabe(
    settlement_id: str,
    payload: SettlementFreigabeRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Freigabe-Schritt für eine Abrechnung (persistiert approval_status im drying_result-JSONB).

    Nutzt evaluate_settlement_approval() aus dem Core-Contract.
    """
    try:
        result = _svc(db, tenant_id).apply_freigabe(
            settlement_id=settlement_id,
            actor_id=payload.actor_id,
            actor_type_str=payload.actor_type,
            target_status_str=payload.target_status,
            reason=payload.reason,
            expected_row_version=payload.expected_row_version,
        )
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.detail)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.detail)
    except ValidationFailedError as exc:
        raise HTTPException(status_code=422, detail=exc.detail)
    return result


@router.post("/{settlement_id}/reject", response_model=dict, tags=["agrar", "settlement", "freigabe"])
async def reject_settlement(
    settlement_id: str,
    actor_id: str = Query(..., description="Benutzer-ID des Ablehnenden"),
    actor_type: str = Query(default="SACHBEARBEITER"),
    reason: str = Query(..., description="Pflichtbegründung für Ablehnung"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Lehnt eine Abrechnung ab — Convenience-Wrapper über POST /{id}/freigabe mit target_status=ABGELEHNT."""
    reject_payload = SettlementFreigabeRequest(
        actor_id=actor_id,
        actor_type=actor_type,
        target_status="ABGELEHNT",
        reason=reason,
    )
    return await settlement_freigabe(settlement_id, reject_payload, tenant_id, db)
