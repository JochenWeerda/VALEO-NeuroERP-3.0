from __future__ import annotations

from typing import Any, List, Optional
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.api.v1.schemas.base import BaseSchema

class HarvestAcceptanceOut(BaseModel):
    """Ernte-Annahme Ausgabe."""
    model_config = {"from_attributes": True}

    id: str
    acceptance_number: str
    tenant_id: str
    branch_id: Optional[str]
    warehouse_id: Optional[str]
    delivery_date: date
    delivery_time: Optional[str]
    sales_rep_id: Optional[str]
    operator_id: str
    weighing_ticket_id: Optional[str]
    cost_center_id: Optional[str]
    customer_id: str
    contract_id: Optional[str]
    forwarder_id: Optional[str]
    intermediate_dealer_id: Optional[str]
    deviating_vat_id: Optional[str]
    article_id: Optional[str]
    variety_id: Optional[str]
    vehicle_plate: Optional[str]
    origin_nuts2_code: Optional[str]
    nuts_version: Optional[str]
    origin_postal_code: Optional[str]
    origin_city: Optional[str]
    origin_country_code: Optional[str]
    is_sustainable_biomass: bool = False
    release_status: str = "draft"
    pricing_mode: str = "spot_daily"
    price_source_id: Optional[str]
    acceptance_mode: Optional[str]
    ownership_type: Optional[str]
    vat_event: Optional[str]
    advance_payment_amount_eur: Optional[float]
    advance_payment_date: Optional[date]
    advance_invoice_id: Optional[str]
    provisional_invoice_number: Optional[str]
    invoice_id: Optional[str]
    invoice_number: Optional[str]
    stock_movement_id: Optional[str]
    quality_protocol_id: Optional[str]
    remarks: Optional[str]
    print_remarks_on_acceptance_note: bool = False
    print_remarks_on_settlement: bool = False
    total_net_amount_eur: Optional[float]
    total_vat_amount_eur: Optional[float]
    total_gross_amount_eur: Optional[float]
    vat_rate_percent: Optional[float]
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_at: Optional[datetime]
    updated_by: Optional[str]

