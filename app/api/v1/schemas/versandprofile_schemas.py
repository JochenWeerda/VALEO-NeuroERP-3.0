"""Auto-generated domain schemas for versandprofile."""
from __future__ import annotations
from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class VersandprofileOut(BaseSchema):
    """Response schema for versandprofile endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class VersandprofilCreate(BaseModel):
    profil_nr: str = Field(..., max_length=20)
    bezeichnung: str
    versandart: str = Field(default="email")
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = Field(None, ge=1, le=65535)
    smtp_benutzer: Optional[str] = None
    absender_email: Optional[str] = None
    absender_name: Optional[str] = None
    cc_email: Optional[str] = None
    bcc_email: Optional[str] = None
    betreff_vorlage: Optional[str] = None
    archiv_kennzeichen: bool = True


class VersandprofilOut(BaseModel):
    id: str
    profil_nr: str
    bezeichnung: str
    versandart: str
    smtp_server: Optional[str]
    smtp_port: Optional[int]
    smtp_benutzer: Optional[str]
    absender_email: Optional[str]
    absender_name: Optional[str]
    cc_email: Optional[str]
    bcc_email: Optional[str]
    betreff_vorlage: Optional[str]
    archiv_kennzeichen: bool
    aktiv: bool
    created_at: datetime


class LieferavisCreate(BaseModel):
    avis_nr: Optional[str] = None
    lieferant_nr: Optional[str] = None
    kunden_nr: Optional[str] = None
    lieferschein_nr: Optional[str] = None
    avis_datum: date
    lieferdatum_erwartet: Optional[date] = None
    artikel_nr: Optional[str] = None
    menge: Optional[Decimal] = Field(None, gt=0)
    mengeneinheit: Optional[str] = None
    notiz: Optional[str] = None


class LieferavisOut(BaseModel):
    id: str
    avis_nr: str
    lieferant_nr: Optional[str]
    kunden_nr: Optional[str]
    lieferschein_nr: Optional[str]
    avis_datum: date
    lieferdatum_erwartet: Optional[date]
    status: str
    artikel_nr: Optional[str]
    menge: Optional[Decimal]
    mengeneinheit: Optional[str]
    notiz: Optional[str]
    created_at: datetime

