from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field


ProviderName = Literal["fiskaly", "swissbit_cloud", "swissbit_gateway", "simulation"]


class FiscalLine(BaseModel):
    text: str
    quantity: Decimal = Decimal("1")
    gross_amount: Decimal
    vat_rate: Decimal


class PaymentLine(BaseModel):
    method: str
    amount: Decimal


class StartTransactionCommand(BaseModel):
    terminal_id: str
    cash_register_id: str
    client_id: str
    transaction_id: str
    transaction_type: str = "RECEIPT"
    lines: list[FiscalLine] = Field(default_factory=list)
    payments: list[PaymentLine] = Field(default_factory=list)
    receipt_number: str | None = None


class FinishTransactionCommand(StartTransactionCommand):
    pass


class FiscalTransactionResult(BaseModel):
    provider: ProviderName
    transaction_id: str
    state: str
    signature: str | None = None
    signature_counter: int | None = None
    serial_number: str | None = None
    qr_code_data: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    provider_reference: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)
    simulated: bool = False


class CashPointClosingCommand(BaseModel):
    closing_id: str
    cash_register_id: str
    terminal_id: str
    business_date: date
    transaction_count: int = Field(ge=0)
    gross_total: Decimal
    payments: list[PaymentLine] = Field(default_factory=list)
    payload: dict[str, Any] = Field(default_factory=dict)


class ExportCommand(BaseModel):
    export_id: str
    cash_register_id: str
    period_from: date
    period_to: date
    export_type: Literal["tse", "dsfinvk"]


class ProviderResult(BaseModel):
    provider: ProviderName
    operation: str
    provider_reference: str | None = None
    status: str
    download_url: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)
    simulated: bool = False


class ProviderReadiness(BaseModel):
    provider: ProviderName
    ready: bool
    live: bool
    blockers: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    details: dict[str, Any] = Field(default_factory=dict)
