"""
VALEO-NeuroERP API v1 Router
Main API router that includes all domain routers
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    tenants,
    users,
    customers,
    leads,
    contacts,
    activities,
    farm_profiles,
    opportunities,
    cases,
    accounts,
    journal_entries,
    articles,
    warehouses,
    policies,
    gap,
    prospecting,
    finance_invoices,
    audit,
    accounting_periods,
    payment_matching,
    ap_invoices,
    bank_accounts,
    debtors,
    open_items,
    bank_statement_import,
    bank_reconciliation,
    tax_keys,
    subsidiary_ledger_reconciliation,
    financial_reports,
    bulk_journal_import,
    exchange_rates,
    booking_templates,
    dunning,
    ap_approval_workflow,
    payment_runs,
    auto_matching,
    vat_return_export,
    closing_checklists,
    iban_lookup,
    credit_debit_memos
)

# Import domain routers
from app.domains.agrar.api import psm, psm_proplanta
from app.documents.router import router as documents_router
from app.reports.router import router as reports_router
from app.verkauf.router import router as verkauf_router

# Create main API router
api_router = APIRouter()


@api_router.get("/status", tags=["meta"])
async def api_status():
    """Lightweight status endpoint for authenticated clients."""
    return {"status": "ok"}

# Include domain routers
api_router.include_router(
    health,
    prefix="/health",
    tags=["health"]
)

api_router.include_router(
    tenants,
    tags=["tenants"]
)

api_router.include_router(
    users,
    tags=["users"]
)

api_router.include_router(
    customers,
    prefix="/crm/customers",
    tags=["crm", "customers"]
)

api_router.include_router(
    leads,
    prefix="/crm/leads",
    tags=["crm", "leads"]
)

api_router.include_router(
    contacts,
    prefix="/crm/contacts",
    tags=["crm", "contacts"]
)

api_router.include_router(
    activities.router,
    prefix="/crm/activities",
    tags=["crm", "activities"]
)

api_router.include_router(
    farm_profiles.router,
    prefix="/crm/farm-profiles",
    tags=["crm", "farm-profiles"]
)

api_router.include_router(
    opportunities.router,
    prefix="/crm/opportunities",
    tags=["crm", "opportunities"]
)

api_router.include_router(
    cases.router,
    prefix="/crm/cases",
    tags=["crm", "cases"]
)

api_router.include_router(
    accounts,
    prefix="/accounts",
    tags=["finance", "accounts"]
)

api_router.include_router(
    journal_entries,
    prefix="/journal-entries",
    tags=["finance", "journal-entries"]
)

api_router.include_router(
    finance_invoices.router,
    tags=["finance", "invoices"]
)

api_router.include_router(
    audit.router,
    prefix="/audit",
    tags=["audit", "compliance", "gobd"]
)

api_router.include_router(
    accounting_periods.router,
    prefix="/finance/periods",
    tags=["finance", "periods", "gobd"]
)

api_router.include_router(
    payment_matching.router,
    prefix="/finance/payments",
    tags=["finance", "payments", "matching", "ar"]
)

api_router.include_router(
    ap_invoices.router,
    prefix="/finance",
    tags=["finance", "ap", "invoices"]
)

api_router.include_router(
    credit_debit_memos.router,
    prefix="/v1",
    tags=["procurement", "ap", "memos"]
)

api_router.include_router(
    debtors.router,
    prefix="/finance",
    tags=["finance", "debtors"]
)

api_router.include_router(
    open_items.router,
    prefix="/finance",
    tags=["finance", "open-items"]
)

api_router.include_router(
    bank_statement_import.router,
    prefix="/finance",
    tags=["finance", "bank-statements"]
)

api_router.include_router(
    bank_reconciliation.router,
    prefix="/finance",
    tags=["finance", "bank-reconciliation"]
)

api_router.include_router(
    tax_keys.router,
    prefix="/finance",
    tags=["finance", "tax"]
)

api_router.include_router(
    subsidiary_ledger_reconciliation.router,
    prefix="/finance",
    tags=["finance", "reconciliation"]
)

api_router.include_router(
    financial_reports.router,
    prefix="/finance",
    tags=["finance", "reports"]
)

api_router.include_router(
    bulk_journal_import.router,
    prefix="/finance",
    tags=["finance", "import"]
)

api_router.include_router(
    exchange_rates.router,
    prefix="/finance",
    tags=["finance", "currency"]
)

api_router.include_router(
    booking_templates.router,
    prefix="/finance",
    tags=["finance", "templates"]
)

api_router.include_router(
    dunning.router,
    prefix="/finance",
    tags=["finance", "dunning"]
)

api_router.include_router(
    ap_approval_workflow.router,
    prefix="/finance",
    tags=["finance", "ap", "approval"]
)

api_router.include_router(
    payment_runs.router,
    prefix="/finance",
    tags=["finance", "ap", "sepa"]
)

api_router.include_router(
    auto_matching.router,
    prefix="/finance",
    tags=["finance", "bank", "matching"]
)

api_router.include_router(
    vat_return_export.router,
    prefix="/finance",
    tags=["finance", "tax", "vat"]
)

api_router.include_router(
    closing_checklists.router,
    prefix="/finance",
    tags=["finance", "closing"]
)

api_router.include_router(
    iban_lookup.router,
    prefix="/finance",
    tags=["finance", "iban", "validation"]
)

api_router.include_router(
    articles,
    prefix="/articles",
    tags=["inventory", "articles"]
)

api_router.include_router(
    warehouses,
    prefix="/warehouses",
    tags=["inventory", "warehouses"]
)

api_router.include_router(
    policies.router,
    prefix="/mcp",
    tags=["mcp", "policies"]
)

api_router.include_router(
    gap.router,
    tags=["gap", "prospecting"]
)

api_router.include_router(
    prospecting.router,
    tags=["prospecting", "leads"]
)

api_router.include_router(
    verkauf_router,
    prefix="/verkauf",
    tags=["verkauf", "kundenstamm"]
)

# Documents and Reports routers
api_router.include_router(
    documents_router,
    tags=["documents", "sales"]
)

api_router.include_router(
    reports_router,
    tags=["reports", "analytics", "dashboard"]
)

# Agrar domain routers
api_router.include_router(
    psm.router,
    prefix="/agrar/psm",
    tags=["agrar", "psm"]
)

api_router.include_router(
    psm_proplanta.router,
    prefix="/agrar/psm/proplanta",
    tags=["agrar", "psm", "proplanta", "integration"]
)
