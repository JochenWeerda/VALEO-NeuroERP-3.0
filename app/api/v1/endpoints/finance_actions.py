"""
Finance action endpoints – Start/run actions for bank reconciliation, posting, cash, direct debit, closing.
Minimal action endpoints that execute a short logic or stub and return { success, message }.
"""

from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from ....core.dependency_container import container
from ....infrastructure.repositories import JournalEntryRepository

router = APIRouter(tags=["finance", "actions"])


class ActionResponse(BaseModel):
    """Standard response for finance actions"""
    success: bool = True
    message: str = ""


class JournalEntryPostRequest(BaseModel):
    """Request to post a journal entry by ID"""
    journal_entry_id: str = Field(..., description="ID der zu buchenden Buchung")


class BankReconciliationRunRequest(BaseModel):
    """Request to run bank reconciliation"""
    bank_account_id: str = Field(..., description="Bankkonto-ID")
    statement_id: Optional[str] = Field(None, description="Optional: Kontoauszug-ID")


# ── Bank reconciliation run ─────────────────────────────────────────────────────

@router.post("/bank-reconciliation/run", response_model=ActionResponse)
async def run_bank_reconciliation(
    body: BankReconciliationRunRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Start Bankabgleich (Abgleich Job anstoßen oder Status setzen).
    Für konkreten Abgleich: GET /finance/bank-reconciliation/{statement_id}/reconcile mit Query-Parametern nutzen.
    """
    # Stub: can be extended to enqueue job or call reconcile logic
    return ActionResponse(
        success=True,
        message=f"Bankabgleich für Konto {body.bank_account_id} angestoßen.",
    )


# ── Journal entry post ─────────────────────────────────────────────────────────

@router.post("/journal-entries/post", response_model=ActionResponse)
async def post_journal_entry_action(
    body: JournalEntryPostRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Buchung buchen (Journal Entry von Entwurf auf gebucht setzen).
    """
    try:
        entry_repo = container.resolve(JournalEntryRepository)
        success = await entry_repo.post_entry(body.journal_entry_id, tenant_id)
        if not success:
            return ActionResponse(success=False, message="Buchung konnte nicht gebucht werden.")
        return ActionResponse(success=True, message="Buchung erfolgreich gebucht.")
    except Exception as e:
        return ActionResponse(success=False, message=f"Fehler beim Buchen: {e!s}")


# ── Cash close day ─────────────────────────────────────────────────────────────

@router.post("/cash/close-day", response_model=ActionResponse)
async def cash_close_day(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Kasse Tagesabschluss (Stub: Status/Job anstoßen).
    """
    # Stub: can be extended to close cash register day, create closing entry, etc.
    return ActionResponse(success=True, message="Kassen-Tagesabschluss angestoßen.")


# ── Direct debit run ───────────────────────────────────────────────────────────

@router.post("/direct-debit/run", response_model=ActionResponse)
async def run_direct_debit(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Lastschriftenlauf starten (Debitoren-Lastschriften; Stub).
    """
    # Stub: can be extended to create SEPA direct debit file, update status
    return ActionResponse(success=True, message="Lastschriftenlauf angestoßen.")


# ── Closing run ───────────────────────────────────────────────────────────────

@router.post("/closing/run", response_model=ActionResponse)
async def run_closing(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    Abschluss (Periodenabschluss) anstoßen (Stub).
    """
    # Stub: can be extended to run period closing, close periods, etc.
    return ActionResponse(success=True, message="Abschluss angestoßen.")
