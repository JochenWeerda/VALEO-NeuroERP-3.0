"""Canonical tax-advisor export profiles.

The service maps VALEO accounting/payroll handoff lines to profile-specific
CSV/ASCII exports. Profiles are not certification claims; they are validation
and mapping contracts that must be accepted by a tax-advisor test import.
"""
from __future__ import annotations

import csv
import hashlib
import io
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

import yaml


PROFILE_DIR = Path("config/export_profiles")
TERMINAL_BATCH_STATUSES = {"exported", "accepted_by_tax_advisor", "rejected", "corrected"}
ALLOWED_BATCH_STATUSES = {"draft", "validated", *TERMINAL_BATCH_STATUSES}


@dataclass(frozen=True)
class AccountingExportLine:
    export_batch_id: str
    tenant_id: str
    external_profile: str
    fiscal_year: int
    period: str
    booking_date: date
    document_date: date
    document_no: str
    document_type: str
    account_no: str
    contra_account_no: str
    debit_credit: str
    amount_net: Decimal
    currency: str
    booking_text: str
    service_date: date | None = None
    amount_gross: Decimal | None = None
    tax_amount: Decimal | None = None
    tax_key: str | None = None
    customer_vendor_no: str | None = None
    cost_center_1: str | None = None
    cost_center_2: str | None = None
    profit_center: str | None = None
    due_date: date | None = None
    payment_terms: str | None = None
    iban: str | None = None
    document_link: str | None = None
    archive_id: str | None = None
    correction_of_export_id: str | None = None
    checksum: str = ""

    def value(self, field_name: str) -> Any:
        return getattr(self, field_name)

    def with_checksum(self) -> "AccountingExportLine":
        payload = "|".join(
            str(getattr(self, name) or "")
            for name in (
                "export_batch_id",
                "tenant_id",
                "external_profile",
                "fiscal_year",
                "period",
                "booking_date",
                "document_date",
                "document_no",
                "document_type",
                "account_no",
                "contra_account_no",
                "debit_credit",
                "amount_net",
                "currency",
                "booking_text",
                "cost_center_1",
                "cost_center_2",
                "correction_of_export_id",
            )
        )
        return AccountingExportLine(**{**self.__dict__, "checksum": hashlib.sha256(payload.encode("utf-8")).hexdigest()})


@dataclass(frozen=True)
class AccountingExportMappingRule:
    target: str
    source: str
    required: bool = False
    fallback: str | None = None


@dataclass(frozen=True)
class AccountingExportProfile:
    id: str
    version: int
    status: str
    strategy: str
    requires_tax_advisor_test_import: bool
    format: dict[str, Any]
    fields: list[AccountingExportMappingRule]
    validation: dict[str, Any] = field(default_factory=dict)
    subprofiles: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AccountingExportValidationResult:
    exportable: bool
    errors: list[str]
    warnings: list[str]


@dataclass(frozen=True)
class AccountingExportBatch:
    id: str
    tenant_id: str
    external_profile: str
    fiscal_year: int
    period: str
    status: str
    lines: list[AccountingExportLine]
    version: int = 1
    correction_of_export_id: str | None = None
    checksum: str = ""
    audit_log: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        *,
        tenant_id: str,
        external_profile: str,
        fiscal_year: int,
        period: str,
        lines: Iterable[AccountingExportLine],
        correction_of_export_id: str | None = None,
    ) -> "AccountingExportBatch":
        batch_id = str(uuid4())
        prepared = [
            AccountingExportLine(
                **{
                    **line.__dict__,
                    "export_batch_id": batch_id,
                    "tenant_id": tenant_id,
                    "external_profile": external_profile,
                    "fiscal_year": fiscal_year,
                    "period": period,
                    "correction_of_export_id": correction_of_export_id,
                }
            ).with_checksum()
            for line in lines
        ]
        checksum = hashlib.sha256("".join(line.checksum for line in prepared).encode("utf-8")).hexdigest()
        return cls(
            id=batch_id,
            tenant_id=tenant_id,
            external_profile=external_profile,
            fiscal_year=fiscal_year,
            period=period,
            status="draft",
            lines=prepared,
            version=1 if correction_of_export_id is None else 2,
            correction_of_export_id=correction_of_export_id,
            checksum=checksum,
            audit_log=[f"created:{batch_id}", "status:draft"],
        )

    def transition(self, new_status: str) -> "AccountingExportBatch":
        if new_status not in ALLOWED_BATCH_STATUSES:
            raise ValueError(f"Unknown export status: {new_status}")
        if self.status in TERMINAL_BATCH_STATUSES and new_status != self.status:
            raise ValueError("Terminal export batches cannot be overwritten; create a correction batch.")
        return AccountingExportBatch(**{**self.__dict__, "status": new_status, "audit_log": [*self.audit_log, f"status:{new_status}"]})

    def correction(self, lines: Iterable[AccountingExportLine]) -> "AccountingExportBatch":
        return AccountingExportBatch.create(
            tenant_id=self.tenant_id,
            external_profile=self.external_profile,
            fiscal_year=self.fiscal_year,
            period=self.period,
            lines=lines,
            correction_of_export_id=self.id,
        )


def load_profile(profile_id: str, profile_dir: Path = PROFILE_DIR) -> AccountingExportProfile:
    matches = sorted(profile_dir.glob(f"{profile_id}.v*.yaml"))
    if not matches:
        raise FileNotFoundError(f"Export profile not found: {profile_id}")
    raw = yaml.safe_load(matches[-1].read_text(encoding="utf-8"))
    return AccountingExportProfile(
        id=raw["id"],
        version=int(raw["version"]),
        status=raw["status"],
        strategy=raw["strategy"],
        requires_tax_advisor_test_import=bool(raw.get("requires_tax_advisor_test_import", True)),
        format=raw["format"],
        fields=[AccountingExportMappingRule(**field) for field in raw["fields"]],
        validation=raw.get("validation", {}),
        subprofiles=raw.get("subprofiles", []),
    )


def validate_batch(batch: AccountingExportBatch, profile: AccountingExportProfile) -> AccountingExportValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    if profile.id != batch.external_profile:
        errors.append("PROFILE_MISMATCH")
    if profile.status == "not_certified" and not profile.requires_tax_advisor_test_import:
        errors.append("NOT_CERTIFIED_REQUIRES_TEST_IMPORT_FLAG")
    if not batch.lines:
        errors.append("EMPTY_BATCH")
    total_debit = Decimal("0")
    total_credit = Decimal("0")
    for index, line in enumerate(batch.lines, start=1):
        prefix = f"line[{index}]"
        if not line.account_no:
            errors.append(f"{prefix}:ACCOUNT_REQUIRED")
        if not line.contra_account_no:
            errors.append(f"{prefix}:CONTRA_ACCOUNT_REQUIRED")
        if line.amount_net == 0 and (line.amount_gross is None or line.amount_gross == 0):
            errors.append(f"{prefix}:NON_ZERO_AMOUNT_REQUIRED")
        if not line.booking_date or not line.document_date:
            errors.append(f"{prefix}:DATE_REQUIRED")
        if line.period != batch.period:
            errors.append(f"{prefix}:PERIOD_MISMATCH")
        if line.external_profile != batch.external_profile:
            errors.append(f"{prefix}:PROFILE_MISMATCH")
        if profile.validation.get("require_kost1_for_payroll") and line.document_type.lower() == "lohn" and not line.cost_center_1:
            errors.append(f"{prefix}:KOST1_REQUIRED_FOR_PAYROLL")
        amount = line.amount_gross if line.amount_gross is not None else line.amount_net
        if line.debit_credit.upper() in {"S", "DEBIT"}:
            total_debit += amount
        elif line.debit_credit.upper() in {"H", "CREDIT"}:
            total_credit += amount
        else:
            errors.append(f"{prefix}:DEBIT_CREDIT_INVALID")
        if not line.checksum:
            warnings.append(f"{prefix}:CHECKSUM_WILL_BE_GENERATED")
    if profile.validation.get("require_balanced_batch") and total_debit != total_credit:
        errors.append("BATCH_NOT_BALANCED")
    return AccountingExportValidationResult(exportable=not errors, errors=errors, warnings=warnings)


def _format_value(value: Any, profile: AccountingExportProfile) -> str:
    if value is None:
        return ""
    if isinstance(value, Decimal):
        text = f"{value:.2f}"
        return text.replace(".", profile.format.get("decimal_separator", "."))
    if isinstance(value, date):
        fmt = profile.format.get("date_format", "YYYY-MM-DD")
        if fmt == "DDMMYYYY":
            return value.strftime("%d%m%Y")
        if fmt == "DD.MM.YYYY":
            return value.strftime("%d.%m.%Y")
        return value.isoformat()
    return str(value)


def map_line(line: AccountingExportLine, profile: AccountingExportProfile) -> dict[str, str]:
    mapped: dict[str, str] = {}
    for rule in profile.fields:
        value = line.value(rule.source)
        if value in (None, "") and rule.fallback:
            value = line.value(rule.fallback)
        if rule.required and value in (None, ""):
            raise ValueError(f"Required field missing for {profile.id}: {rule.source}")
        mapped[rule.target] = _format_value(value, profile)
    if "checksum" not in {rule.source for rule in profile.fields}:
        mapped["checksum"] = line.checksum
    return mapped


def render_csv(batch: AccountingExportBatch, profile: AccountingExportProfile) -> str:
    validation = validate_batch(batch, profile)
    if not validation.exportable:
        raise ValueError(";".join(validation.errors))
    output = io.StringIO()
    fieldnames = [rule.target for rule in profile.fields]
    if "checksum" not in fieldnames:
        fieldnames.append("checksum")
    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        delimiter=profile.format.get("delimiter", ";"),
        lineterminator="\n",
    )
    if profile.format.get("header_included", True):
        writer.writeheader()
    for line in batch.lines:
        writer.writerow(map_line(line.with_checksum(), profile))
    return output.getvalue()
