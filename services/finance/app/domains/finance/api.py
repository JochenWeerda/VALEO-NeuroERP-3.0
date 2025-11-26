"""FastAPI router for Finance endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from services.finance.app.core.config import settings
from services.finance.app.core.database import get_db
from services.finance.app.domains.finance.schemas import (
    AccountsResponse,
    JournalEntriesResponse,
    JournalEntryCreate,
    JournalEntryResponse,
    OpenItemsResponse,
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

