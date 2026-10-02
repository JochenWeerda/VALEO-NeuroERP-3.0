"""One typed, decimal bank comparison contract; unavailable is never zero."""
from datetime import date
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator


class BankSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class BalanceComparison(BankSchema):
    bank_statement_balance: Decimal | None
    accounting_balance: Decimal | None
    statement_date: date
    comparison_date: date
    currency: str = Field(pattern=r"^[A-Z]{3}$")
    ledger_account_id: str | None
    bank_balance_state: Literal["BANK_PROVIDED", "CSV_SYNTHETIC"]
    accounting_state: Literal["AVAILABLE", "MAPPING_REQUIRED", "NO_POSTED_ENTRIES"]

    @model_validator(mode="after")
    def require_evidence(self):
        if (self.bank_statement_balance is not None) != (self.bank_balance_state == "BANK_PROVIDED"):
            raise ValueError("Bank balance requires bank-provided evidence")
        if (self.accounting_balance is not None) != (self.accounting_state == "AVAILABLE"):
            raise ValueError("Accounting balance requires posted journal evidence")
        if bool(self.ledger_account_id) == (self.accounting_state == "MAPPING_REQUIRED"):
            raise ValueError("Accounting evidence requires an explicit ledger link")
        for value in (self.bank_statement_balance, self.accounting_balance):
            if value is not None and value != value.quantize(Decimal("0.01")):
                raise ValueError("Balances require exact currency cents")
        return self

    @computed_field
    @property
    def difference(self) -> Decimal | None:
        if self.bank_statement_balance is None or self.accounting_balance is None:
            return None
        return self.bank_statement_balance - self.accounting_balance

    @computed_field
    @property
    def is_balanced(self) -> bool:
        return self.difference is not None and self.difference == 0


class DifferenceItem(BankSchema):
    item_type: Literal["UNMATCHED_STATEMENT", "PARTIAL_STATEMENT", "UNKNOWN_STATEMENT_STATUS", "BALANCE_MISMATCH"]
    statement_line_id: str | None = None
    journal_entry_id: str | None = None
    date: date
    amount: Decimal
    bank_amount: Decimal | None = None
    accounting_amount: Decimal | None = None
    reference: str | None = None
    description: str
    suggested_account: Literal[None] = None
    suggested_action: Literal["INVESTIGATE"] = "INVESTIGATE"

    @model_validator(mode="after")
    def consistent_amount(self):
        if self.item_type == "BALANCE_MISMATCH":
            if self.bank_amount is None or self.accounting_amount is None or self.amount != self.bank_amount-self.accounting_amount:
                raise ValueError("Balance discrepancy must equal bank minus accounting")
        elif self.statement_line_id is None or self.bank_amount != self.amount:
            raise ValueError("Unresolved statement discrepancy needs a line and its bank amount")
        return self


class LineCounts(BankSchema):
    total: int
    matched: int
    unmatched: int
    partial: int
    unknown: int

    @model_validator(mode="after")
    def consistent_counts(self):
        if min(self.total, self.matched, self.unmatched, self.partial, self.unknown) < 0:
            raise ValueError("Negative line count")
        if self.total != self.matched + self.unmatched + self.partial + self.unknown:
            raise ValueError("Contradictory line counts")
        return self


class ReconciliationResult(BankSchema):
    statement_id: str
    bank_account_id: str
    balance_comparison: BalanceComparison
    differences: list[DifferenceItem]
    total_differences: int
    line_counts: LineCounts
    can_be_booked: Literal[False] = False
    differences_offset: int = 0
    differences_limit: int = 100

    @model_validator(mode="after")
    def consistent_differences(self):
        unresolved = self.line_counts.unmatched + self.line_counts.partial + self.line_counts.unknown
        mismatch = self.balance_comparison.difference is not None and self.balance_comparison.difference != 0
        if self.total_differences != unresolved + int(mismatch):
            raise ValueError("Contradictory difference count")
        if not 1 <= self.differences_limit <= 100 or self.differences_offset < 0:
            raise ValueError("Invalid difference page")
        if len(self.differences) > min(self.differences_limit, self.total_differences):
            raise ValueError("Difference page exceeds total or limit")
        return self

    @computed_field
    @property
    def comparison_state(self) -> Literal["INCOMPLETE", "DIFFERENCES", "BALANCES_EQUAL"]:
        balance = self.balance_comparison
        if balance.difference is None or self.line_counts.partial or self.line_counts.unknown:
            return "INCOMPLETE"
        if not balance.is_balanced or self.line_counts.unmatched:
            return "DIFFERENCES"
        return "BALANCES_EQUAL"
