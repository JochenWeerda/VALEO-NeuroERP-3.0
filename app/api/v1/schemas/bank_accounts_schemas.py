"""Canonical bank-account contracts with an explicit ledger ID."""
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class BankAccountBase(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    account_number: str = Field(min_length=1, max_length=50)
    bank_name: str = Field(min_length=1, max_length=255)
    iban: Optional[str] = None
    bic: Optional[str] = None
    currency: str = Field(default="EUR", pattern=r"^[A-Z]{3}$")
    gl_account_id: Optional[str] = None
    is_active: bool = True


class BankAccountCreate(BankAccountBase):
    pass


class BankAccountUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    bank_name: Optional[str] = None
    iban: Optional[str] = None
    bic: Optional[str] = None
    currency: Optional[str] = Field(default=None, pattern=r"^[A-Z]{3}$")
    gl_account_id: Optional[str] = None
    is_active: Optional[bool] = None


class BankAccountResponse(BankAccountBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    balance: Optional[Decimal] = None


class BankAccountsOut(BankAccountBase):
    """Create template uses the same field vocabulary as bank accounts."""
    account_number: str = ""
    bank_name: str = ""
    id: str | None = None
    tenant_id: str
    balance: Decimal | None = None


class BankLedgerOption(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    id: str
    account_number: str
    account_name: str
