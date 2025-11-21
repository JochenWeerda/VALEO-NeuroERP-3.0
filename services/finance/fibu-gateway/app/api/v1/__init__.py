from fastapi import APIRouter

from .routes import approval_rules, chart_of_accounts, journal_entries, op_management

router = APIRouter(prefix="/finance", tags=["finance"])
router.include_router(chart_of_accounts.router)
router.include_router(journal_entries.router)
router.include_router(op_management.router)
router.include_router(approval_rules.router)

__all__ = ["router"]

