"""Pydantic schemas for the banken domain."""
from __future__ import annotations

from typing import Any, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.api.v1.schemas.base import BaseSchema


class BankenOut(BaseSchema):
    """Typed response schema for BankenOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


class BankKontoCreate(BaseModel):
    iban: str = Field(..., description="IBAN")
    bic: str = Field(..., description="BIC/SWIFT")
    bank_name: str = Field(..., description="Bank name")
    kontoart: str = Field(..., description="Account type")
    waehrung: str = Field(default="EUR")
    ist_aktiv: bool = Field(default=True)
    saldo: float = Field(default=0)


class BankKontoUpdate(BaseModel):
    bank_name: Optional[str] = None
    kontoart: Optional[str] = None
    ist_aktiv: Optional[bool] = None
    status: Optional[str] = None
    saldo: Optional[float] = None


class UeberweisungRequest(BaseModel):
    auftraggeber_iban: str
    empfaenger_iban: str
    empfaenger_name: str
    betrag: float = Field(..., gt=0)
    verwendungszweck: str = Field(..., max_length=140)
    blz: str = ""
    user_id: str = ""
    pin: str = Field("", description="Nur für einmalige Übertragung — empfohlen: Env-Var FINTS_PIN")


class TanInitRequest(BaseModel):
    auftraggeber_iban: str
    empfaenger_iban: str
    empfaenger_name: str
    betrag: float
    verwendungszweck: str
    tan_verfahren_id: str = ""
    blz: str = ""
    user_id: str = ""
    pin: str = ""


class TanBestaetigenRequest(BaseModel):
    session_token: str
    tan: str
    blz: str = ""
    user_id: str = ""
    pin: str = ""

