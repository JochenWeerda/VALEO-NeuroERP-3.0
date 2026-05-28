"""Pydantic schemas for the Agrar domain.

Covers harvest acceptance, settlements, quality protocols, freight costs, NUTS-2 derivation.
Import these in endpoint files and service files instead of using CompatFlexOut.
"""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


# ── Harvest Settlement ────────────────────────────────────────────────────────

class HarvestSettlementPositionOut(BaseModel):
    position_number: int
    description: Optional[str] = None
    quantity_kg: Optional[float] = None
    quantity_pct: Optional[float] = None
    amount_eur: Optional[float] = None
    unit: Optional[str] = None
    calculation_formula: Optional[str] = None


class HarvestSettlementOut(BaseModel):
    acceptance_id: str
    positions: list[HarvestSettlementPositionOut]
    total_net_amount_eur: float
    total_vat_amount_eur: float
    total_gross_amount_eur: float
    vat_rate_percent: Optional[float] = None
    warnings: list[str] = Field(default_factory=list)
    price_source: str


# ── NUTS-2 Derivation ─────────────────────────────────────────────────────────

class Nuts2DeriveOut(BaseModel):
    origin_nuts2_code: Optional[str] = None
    nuts_version: Optional[str] = None
    message: str


# ── Quality Protocol ─────────────────────────────────────────────────────────

class QualityProtocolOut(BaseModel):
    model_config = {"extra": "allow"}


class QualityProtocolCreateOut(BaseModel):
    message: str
    qualitaetsprotokoll: QualityProtocolOut
    quality_status: Optional[str] = None


# ── Freight Costs ─────────────────────────────────────────────────────────────

class FrachtkostenCalculateOut(BaseModel):
    acceptance_id: str
    entfernung_km: float
    gewicht_kg: float
    gewicht_tonnen: float
    frachtkosten_eur: float


class FrachtkostenOut(BaseModel):
    acceptance_id: str
    frachtkosten_eur: float


# ── Agrar Settlements (self-billing) ─────────────────────────────────────────

class SettlementDeductionOut(BaseModel):
    id: str
    settlement_id: str
    deduction_type: str
    mode: str
    rate_per_ton_eur: Optional[float] = None
    fixed_amount_eur: Optional[float] = None
    quantity_tons: Optional[float] = None
    total_eur: Optional[float] = None
    description: Optional[str] = None
    created_at: Optional[str] = None


class SettlementOut(BaseModel):
    id: str
    tenant_id: str
    farmer_id: str
    contract_id: Optional[str] = None
    article_id: Optional[str] = None
    delivery_date: Optional[str] = None
    quantity_delivered_tons: Optional[float] = None
    gross_price_eur_per_ton: Optional[float] = None
    gross_amount_eur: Optional[float] = None
    net_amount_eur: Optional[float] = None
    vat_rate_percent: Optional[float] = None
    vat_amount_eur: Optional[float] = None
    total_gross_eur: Optional[float] = None
    status: str
    posted_at: Optional[str] = None
    credit_note_number: Optional[str] = None
    deductions: list[SettlementDeductionOut] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class SettlementApproveOut(BaseModel):
    id: str
    status: str
    posted_at: Optional[str] = None
    credit_note_number: Optional[str] = None
    message: str


class SettlementDryingResultOut(BaseModel):
    settlement_id: str
    drying_deduction_eur: Optional[float] = None
    drying_rule_applied: Optional[str] = None
    message: str


class SettlementPdfOut(BaseModel):
    settlement_id: str
    pdf_url: Optional[str] = None
    pdf_base64: Optional[str] = None
    filename: str
    message: str


# ── Sales Order ──────────────────────────────────────────────────────────────

class DeliveryNoteCreatedOut(BaseModel):
    ok: bool
    delivery_note_id: str
    delivery_note_number: str
    order_id: str


# ── Sales Lines ───────────────────────────────────────────────────────────────

class SalesOrderLineOut(BaseModel):
    id: str
    line_number: int
    article_number: Optional[str] = None
    description: Optional[str] = None
    quantity: float
    unit: Optional[str] = None
    unit_price: float
    discount_percent: float = 0.0
    tax_rate: float = 0.0
    line_total_net: float
    line_total_tax: float
    line_total_gross: float


class SalesOrderOut(BaseModel):
    id: str
    tenant_id: str
    order_number: Optional[str] = None
    customer_id: Optional[str] = None
    order_date: Optional[str] = None
    delivery_date: Optional[str] = None
    status: str
    payment_terms: Optional[str] = None
    total_net: float = 0.0
    total_tax: float = 0.0
    total_gross: float = 0.0
    lines: list[SalesOrderLineOut] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
