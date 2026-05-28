"""Auto-generated domain schemas for admin pos.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class AdminPosOut(BaseSchema):
    """Response schema for admin pos endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class PosTerminalIn(BaseModel):
    terminal_code: str = Field(..., min_length=1, max_length=60)
    name: str = Field(..., min_length=1, max_length=120)
    location_name: Optional[str] = Field(default=None, max_length=120)
    branch_code: Optional[str] = Field(default=None, max_length=60)
    is_active: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class PosTerminalOut(PosTerminalIn):
    id: str
    registered_at: Optional[datetime] = None
    unregistered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class PosTseDeviceIn(BaseModel):
    terminal_id: str
    serial_number: str = Field(..., min_length=1, max_length=120)
    provider: Optional[str] = Field(default=None, max_length=120)
    api_endpoint: Optional[str] = Field(default=None, max_length=255)
    certificate_fingerprint: Optional[str] = Field(default=None, max_length=255)
    status: str = Field(default="active", pattern="^(active|inactive|retired)$")
    activation_date: Optional[date] = None
    deactivation_date: Optional[date] = None
    last_heartbeat_at: Optional[datetime] = None
    settings: dict[str, Any] = Field(default_factory=dict)


class PosTseDeviceOut(PosTseDeviceIn):
    id: str
    created_at: datetime
    updated_at: datetime


class PosNoticeIn(BaseModel):
    terminal_id: Optional[str] = None
    tse_device_id: Optional[str] = None
    notice_type: str = Field(..., pattern="^(install|change|decommission)$")
    notice_status: str = Field(default="draft", pattern="^(draft|submitted|accepted|rejected)$")
    effective_date: date
    submitted_at: Optional[datetime] = None
    reference_number: Optional[str] = Field(default=None, max_length=120)
    payload: dict[str, Any] = Field(default_factory=dict)


class PosNoticeOut(PosNoticeIn):
    id: str
    created_at: datetime
    updated_at: datetime


class DsfinvkExportRequest(BaseModel):
    period_from: date
    period_to: date
    generated_by: Optional[str] = Field(default=None, max_length=100)


class DsfinvkExportOut(BaseModel):
    id: str
    tenant_id: str
    period_from: date
    period_to: date
    status: str
    file_path: Optional[str] = None
    checksum_sha256: Optional[str] = None
    row_count: int
    generated_by: Optional[str] = None
    generated_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class KasseUebernahmeRequest(BaseModel):
    """Datentypen die aus der ServiceERP-Kasse übernommen werden sollen."""
    artikel_umsaetze_kompr: bool = Field(True, description="Artikel-Umsätze komprimiert (UM*.db)")
    artikel_umsaetze_einzeln: bool = Field(True, description="Artikel-Umsätze einzeln (UEZ*.db)")
    umsaetze_lieferscheine: bool = Field(True, description="Umsätze aus Lieferscheinen (UL*.db)")
    einnahmen_ausgaben: bool = Field(True, description="Einnahmen / Ausgaben (EA*.db)")
    serien_nummern: bool = Field(True, description="Serien-Nummern (SE*.db)")
    gutscheine: bool = Field(True, description="Gutscheine (GU*.db)")


class TseTransactionRequest(BaseModel):
    tss_id: str
    client_id: str
    amount_cents: int = Field(..., gt=0, description="Betrag in Cent")
    payment_type: str = "Unbar"


class TseFinishRequest(BaseModel):
    tss_id: str
    tx_id: str
    amount_cents: int
    counter: int = 1

