"""
Versioned Agrar integration event contracts (v1).
"""

from datetime import datetime
from typing import Any, Dict, Literal

from pydantic import BaseModel, Field


EVENT_CONTRACT_VERSION = "1.0.0"


class BaseAgrarEventV1(BaseModel):
    event_id: str = Field(..., description="Unique event identifier")
    event_type: str = Field(..., description="Canonical event type name")
    event_version: str = Field(default=EVENT_CONTRACT_VERSION, description="Contract version")
    aggregate_id: str = Field(..., description="Business aggregate id")
    tenant_id: str = Field(..., description="Tenant context id")
    occurred_at: datetime = Field(..., description="Event timestamp UTC")
    correlation_id: str | None = Field(default=None, description="Cross-service correlation id")


class WeighingTicketCreatedV1(BaseAgrarEventV1):
    event_type: Literal["agrar.weighing_ticket.created"] = "agrar.weighing_ticket.created"
    ticket_number: str
    gross_weight_kg: float
    tare_weight_kg: float
    net_weight_kg: float
    quality: Dict[str, Any] = Field(
        default_factory=dict,
        description="Quality values, e.g. moisture/protein/besatz/hl_weight",
    )


class ContractAllocatedV1(BaseAgrarEventV1):
    event_type: Literal["agrar.contract.allocated"] = "agrar.contract.allocated"
    contract_id: str
    contract_number: str
    allocation_quantity_kg: float
    remaining_quantity_kg: float
    pricing_model: Literal["fixed", "follow", "pool"]


class WeighingTicketAllocatedV1(BaseAgrarEventV1):
    event_type: Literal["agrar.weighing_ticket.allocated"] = "agrar.weighing_ticket.allocated"
    contract_id: str
    allocation_id: str
    allocation_quantity_kg: float
    remaining_quantity_kg: float


class SettlementIssuedV1(BaseAgrarEventV1):
    event_type: Literal["agrar.settlement.issued"] = "agrar.settlement.issued"
    settlement_id: str
    settlement_number: str
    base_quantity_kg: float
    billable_quantity_kg: float
    gross_amount: float
    deductions_amount: float
    net_amount: float
    currency: str = "EUR"


AGRAR_EVENT_CONTRACTS_V1 = {
    "agrar.weighing_ticket.created": WeighingTicketCreatedV1,
    "agrar.weighing_ticket.allocated": WeighingTicketAllocatedV1,
    "agrar.contract.allocated": ContractAllocatedV1,
    "agrar.settlement.issued": SettlementIssuedV1,
}

