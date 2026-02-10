"""
Finance Domain Pydantic Schemas
Data validation and serialization schemas for finance domain
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from uuid import UUID


# Account Schemas
class AccountBase(BaseModel):
    """Base account schema"""
    account_number: str = Field(..., min_length=1, max_length=20, description="Account number")
    account_name: str = Field(..., min_length=1, max_length=100, description="Account name")
    account_type: str = Field(..., description="Account type (asset, liability, equity, revenue, expense)")
    category: str = Field(..., description="Account category")
    currency: str = Field(default="EUR", min_length=3, max_length=3, description="Currency code")
    allow_manual_entries: bool = Field(default=True, description="Allow manual journal entries")
    parent_account_id: Optional[str] = Field(None, description="Parent account ID for hierarchy")

    @field_validator('account_type')
    @classmethod
    def validate_account_type(cls, v):
        valid_types = ['asset', 'liability', 'equity', 'revenue', 'expense']
        if v not in valid_types:
            raise ValueError(f'Account type must be one of: {valid_types}')
        return v

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        valid_categories = [
            'current_assets', 'fixed_assets', 'current_liabilities', 'long_term_liabilities',
            'equity', 'revenue', 'cost_of_goods_sold', 'operating_expenses', 'other_expenses'
        ]
        if v not in valid_categories:
            raise ValueError(f'Category must be one of: {valid_categories}')
        return v


class AccountCreate(AccountBase):
    """Schema for creating accounts"""
    tenant_id: str = Field(..., description="Tenant ID")
    parent_account_id: Optional[str] = Field(None, description="Parent account ID for hierarchy")


class AccountUpdate(BaseModel):
    """Schema for updating accounts"""
    account_name: Optional[str] = Field(None, min_length=1, max_length=100)
    account_type: Optional[str] = None
    category: Optional[str] = None
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    allow_manual_entries: Optional[bool] = None


class Account(AccountBase):
    """Full account schema"""
    id: UUID
    tenant_id: str
    balance: Decimal = Field(default=Decimal('0.00'), description="Current balance")
    is_active: bool = Field(default=True, description="Account status")
    parent_account_id: Optional[str] = Field(None, description="Parent account ID for hierarchy")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AccountHierarchy(Account):
    """Account with hierarchy information"""
    children: List['AccountHierarchy'] = Field(default_factory=list, description="Child accounts")


# Journal Entry Line Schemas
class JournalEntryLineBase(BaseModel):
    """Base journal entry line schema"""
    account_id: str = Field(..., description="Account ID")
    debit_amount: Decimal = Field(default=Decimal('0.00'), ge=0, description="Debit amount")
    credit_amount: Decimal = Field(default=Decimal('0.00'), ge=0, description="Credit amount")
    line_number: int = Field(..., gt=0, description="Line number in entry")
    description: Optional[str] = Field(None, max_length=200, description="Line description")
    tax_code: Optional[str] = Field(None, max_length=20, description="Tax code")
    tax_amount: Decimal = Field(default=Decimal('0.00'), ge=0, description="Tax amount")
    cost_center: Optional[str] = Field(None, max_length=50, description="Cost center")
    profit_center: Optional[str] = Field(None, max_length=50, description="Profit center")
    segment: Optional[str] = Field(None, max_length=50, description="Segment")

    @field_validator('debit_amount', 'credit_amount', 'tax_amount')
    @classmethod
    def validate_amounts(cls, v):
        # Ensure amounts have at most 2 decimal places
        if v != v.quantize(Decimal('0.01')):
            raise ValueError('Amount must have at most 2 decimal places')
        return v

    @field_validator('debit_amount', 'credit_amount')
    @classmethod
    def validate_line_amounts(cls, v, info):
        # Either debit or credit must be zero, but not both
        if info.field_name == 'debit_amount':
            credit_amount = info.data.get('credit_amount', Decimal('0.00'))
            if v > 0 and credit_amount > 0:
                raise ValueError('Line cannot have both debit and credit amounts')
        elif info.field_name == 'credit_amount':
            debit_amount = info.data.get('debit_amount', Decimal('0.00'))
            if v > 0 and debit_amount > 0:
                raise ValueError('Line cannot have both debit and credit amounts')
        return v


class JournalEntryLineCreate(JournalEntryLineBase):
    """Schema for creating journal entry lines"""
    pass


class JournalEntryLine(JournalEntryLineBase):
    """Full journal entry line schema"""
    id: UUID
    tenant_id: str
    journal_entry_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Journal Entry Schemas
class JournalEntryBase(BaseModel):
    """Base journal entry schema"""
    entry_number: str = Field(..., min_length=1, max_length=50, description="Entry number")
    entry_date: datetime = Field(..., description="Entry date")
    posting_date: datetime = Field(..., description="Posting date")
    description: str = Field(..., min_length=1, max_length=500, description="Entry description")
    reference: Optional[str] = Field(None, max_length=100, description="Reference document")
    source: str = Field(default="manual", description="Entry source (manual, system, integration)")
    currency: str = Field(default="EUR", min_length=3, max_length=3, description="Currency code")
    lines: List[JournalEntryLineCreate] = Field(..., min_items=2, description="Journal entry lines")

    @field_validator('source')
    @classmethod
    def validate_source(cls, v):
        valid_sources = ['manual', 'system', 'integration', 'import']
        if v not in valid_sources:
            raise ValueError(f'Source must be one of: {valid_sources}')
        return v

    @field_validator('posting_date')
    @classmethod
    def validate_posting_date(cls, v, info):
        entry_date = info.data.get('entry_date')
        if entry_date and v < entry_date:
            raise ValueError('Posting date cannot be before entry date')
        return v


class JournalEntryCreate(JournalEntryBase):
    """Schema for creating journal entries"""
    tenant_id: str = Field(..., description="Tenant ID")


class JournalEntryUpdate(BaseModel):
    """Schema for updating journal entries"""
    entry_date: Optional[datetime] = None
    posting_date: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=500)
    reference: Optional[str] = Field(None, max_length=100)


class JournalEntry(JournalEntryBase):
    """Full journal entry schema"""
    id: UUID
    tenant_id: str
    status: str = Field(default="draft", description="Entry status")
    total_debit: Decimal = Field(default=Decimal('0.00'), description="Total debit amount")
    total_credit: Decimal = Field(default=Decimal('0.00'), description="Total credit amount")
    posted_by: Optional[str] = None
    posted_at: Optional[datetime] = None
    reversal_of: Optional[str] = None
    reversal_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    lines: List[JournalEntryLine] = []

    class Config:
        from_attributes = True


# Financial Reporting Schemas
class AccountBalance(BaseModel):
    """Account balance information"""
    account_id: str
    account_number: str
    account_name: str
    balance: Decimal
    currency: str
    as_of_date: datetime


class TrialBalance(BaseModel):
    """Trial balance report"""
    tenant_id: str
    period_start: datetime
    period_end: datetime
    accounts: List[AccountBalance]
    total_debit: Decimal
    total_credit: Decimal
    in_balance: bool


class GeneralLedgerEntry(BaseModel):
    """General ledger entry for reporting"""
    entry_id: str
    entry_number: str
    entry_date: datetime
    account_number: str
    account_name: str
    description: str
    debit_amount: Decimal
    credit_amount: Decimal
    balance: Decimal
    reference: Optional[str] = None


# Bank Account Schemas
class BankAccountBase(BaseModel):
    """Base bank account schema"""
    account_number: str = Field(..., min_length=1, max_length=50, description="Bank account number")
    bank_name: str = Field(..., min_length=1, max_length=255, description="Bank name")
    iban: Optional[str] = Field(None, max_length=34, description="IBAN")
    bic: Optional[str] = Field(None, max_length=11, description="BIC/SWIFT code")
    currency: str = Field(default="EUR", min_length=3, max_length=3, description="Currency code")
    balance: Decimal = Field(default=Decimal('0.00'), description="Current balance")
    is_active: bool = Field(default=True, description="Account status")


class BankAccountCreate(BankAccountBase):
    """Schema for creating bank accounts"""
    tenant_id: str = Field(..., description="Tenant ID")


class BankAccountUpdate(BaseModel):
    """Schema for updating bank accounts"""
    bank_name: Optional[str] = Field(None, min_length=1, max_length=255)
    iban: Optional[str] = Field(None, max_length=34)
    bic: Optional[str] = Field(None, max_length=11)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    balance: Optional[Decimal] = None
    is_active: Optional[bool] = None


class BankAccount(BankAccountBase):
    """Full bank account schema"""
    id: str
    tenant_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Debtor Schemas
class DebtorBase(BaseModel):
    """Base debtor schema"""
    debtor_number: str = Field(..., min_length=1, max_length=50, description="Debtor number")
    company_name: str = Field(..., min_length=1, max_length=255, description="Company name")
    contact_person: Optional[str] = Field(None, max_length=255, description="Contact person")
    street: str = Field(..., min_length=1, max_length=255, description="Street address")
    postal_code: str = Field(..., min_length=1, max_length=10, description="Postal code")
    city: str = Field(..., min_length=1, max_length=100, description="City")
    country: str = Field(default="DE", min_length=2, max_length=2, description="Country code")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    email: Optional[str] = Field(None, max_length=255, description="Email address")
    vat_id: Optional[str] = Field(None, max_length=50, description="VAT ID")
    tax_number: Optional[str] = Field(None, max_length=50, description="Tax number")
    iban: Optional[str] = Field(None, max_length=34, description="IBAN")
    bic: Optional[str] = Field(None, max_length=11, description="BIC/SWIFT code")
    bank_name: Optional[str] = Field(None, max_length=255, description="Bank name")
    account_holder: Optional[str] = Field(None, max_length=255, description="Account holder")
    payment_terms_days: int = Field(default=30, ge=0, description="Payment terms in days")
    discount_days: int = Field(default=0, ge=0, description="Discount days")
    discount_percent: Decimal = Field(default=Decimal('0.00'), ge=0, le=100, description="Discount percentage")
    credit_limit: Decimal = Field(default=Decimal('0.00'), ge=0, description="Credit limit")
    is_active: bool = Field(default=True, description="Debtor status")
    notes: Optional[str] = Field(None, description="Internal notes")


class DebtorCreate(DebtorBase):
    """Schema for creating debtors"""
    tenant_id: str = Field(..., description="Tenant ID")


class DebtorUpdate(BaseModel):
    """Schema for updating debtors"""
    company_name: Optional[str] = Field(None, min_length=1, max_length=255)
    contact_person: Optional[str] = Field(None, max_length=255)
    street: Optional[str] = Field(None, min_length=1, max_length=255)
    postal_code: Optional[str] = Field(None, min_length=1, max_length=10)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    vat_id: Optional[str] = Field(None, max_length=50)
    tax_number: Optional[str] = Field(None, max_length=50)
    iban: Optional[str] = Field(None, max_length=34)
    bic: Optional[str] = Field(None, max_length=11)
    bank_name: Optional[str] = Field(None, max_length=255)
    account_holder: Optional[str] = Field(None, max_length=255)
    payment_terms_days: Optional[int] = Field(None, ge=0)
    discount_days: Optional[int] = Field(None, ge=0)
    discount_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    credit_limit: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class Debtor(DebtorBase):
    """Full debtor schema"""
    id: str
    tenant_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True