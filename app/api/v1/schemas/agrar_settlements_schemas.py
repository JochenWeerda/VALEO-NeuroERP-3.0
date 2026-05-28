"""Pydantic schemas for the agrar settlements domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class AgrarSettlementOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


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

