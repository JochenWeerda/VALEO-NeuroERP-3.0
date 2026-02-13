"""FastAPI router for Finance endpoints."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Header, Query, Request
from sqlalchemy.orm import Session

from services.finance.app.core.config import settings
from services.finance.app.core.database import get_db
from services.finance.app.domains.finance.schemas import (
    AccountsResponse,
    GoBDComplianceResponse,
    GoBDMonthlyReport,
    JournalEntriesResponse,
    JournalEntryCreate,
    JournalEntryResponse,
    OpenItemsResponse,
    StornoRequest,
    StornoResult,
)
from services.finance.app.domains.finance.service import FinanceService

router = APIRouter()


def get_tenant_id(x_tenant_id: str | None = Header(default=None)) -> str:
    return x_tenant_id or settings.DEFAULT_TENANT


def get_finance_service(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> FinanceService:
    return FinanceService(db=db, tenant_id=tenant_id)


@router.get("/chart-of-accounts", response_model=AccountsResponse)
def list_accounts(service: FinanceService = Depends(get_finance_service)):
    accounts = service.list_accounts()
    return AccountsResponse(items=accounts)


@router.get("/journal-entries", response_model=JournalEntriesResponse)
def list_journal_entries(service: FinanceService = Depends(get_finance_service)):
    entries = service.list_journal_entries()
    return JournalEntriesResponse(items=entries)


@router.post(
    "/journal-entries",
    response_model=JournalEntryResponse,
    status_code=201,
)
def create_journal_entry(
    payload: JournalEntryCreate,
    service: FinanceService = Depends(get_finance_service),
):
    entry, audit_hash = service.create_journal_entry(payload)
    return JournalEntryResponse(entry=entry, audit_hash=audit_hash)


@router.get("/open-items", response_model=OpenItemsResponse)
def list_open_items(service: FinanceService = Depends(get_finance_service)):
    items = service.list_open_items()
    return OpenItemsResponse(items=items)


@router.get("/gobd-compliance", response_model=GoBDComplianceResponse)
def check_gobd_compliance(service: FinanceService = Depends(get_finance_service)):
    """GoBD compliance check: verifies gapless document numbering and audit hash chain integrity.

    Checks:
    1. Lückenlose Belegnummerierung (gapless document numbering)
    2. Hash-Ketten-Integrität (audit trail hash chain)

    Returns a detailed report with any gaps found and an overall compliance status.
    """
    return service.check_gobd_compliance()


@router.get("/gobd-monthly-report", response_model=GoBDMonthlyReport)
def generate_gobd_monthly_report(
    period: str = Query(
        default=None,
        pattern=r"^\d{4}-\d{2}$",
        description="Accounting period (YYYY-MM). Defaults to current month.",
    ),
    service: FinanceService = Depends(get_finance_service),
):
    """Generate a comprehensive monthly GoBD compliance report.

    Includes:
    - Document number gap analysis
    - Audit hash chain validation
    - Cancellation / reversal completeness check
    - Period completeness verification
    - Overall compliance score (0-100)
    - Actionable recommendations

    The report is signed with a SHA-256 hash for integrity verification.
    """
    if period is None:
        period = datetime.utcnow().strftime("%Y-%m")
    return service.generate_monthly_report(period)


@router.post(
    "/journal-entries/storno",
    response_model=StornoResult,
    status_code=200,
)
def cancel_journal_entry(
    payload: StornoRequest,
    service: FinanceService = Depends(get_finance_service),
):
    """Storniere eine Buchung mit automatischer Gegenbuchung (GoBD-konform).

    GoBD §146 AO: Buchungen dürfen nicht gelöscht oder verändert werden.
    Stattdessen wird eine Gegenbuchung mit dem negierten Betrag erstellt.

    Die Gegenbuchung:
    - Referenziert die Original-Buchung via document_id
    - Hat den negierten Betrag
    - Wird im Audit-Trail mit Hash-Chain gesichert
    - Enthält den Storno-Grund

    Raises:
        400: Buchung nicht gefunden oder bereits storniert
    """
    try:
        return service.cancel_journal_entry(
            journal_entry_id=payload.journal_entry_id,
            reason=payload.reason,
            user_id=payload.user_id,
        )
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))
