"""
VALEO-NeuroERP API v1 Router
Main API router that includes all domain routers
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    export_service,
    agrar_feldbuch,
    agrar_wetter,
    agrar_maschinen,
    portal_feldbuch,
    health,
    tenants,
    users,
    customers,
    crm_reports,
    leads,
    contacts,
    activities,
    farm_profiles,
    opportunities,
    cases,
    accounts,
    journal_entries,
    articles,
    sales_orders,
    sales_offers,
    docflow,
    warehouses,
    policies,
    gap,
    prospecting,
    finance_invoices,
    vat_codes,
    audit,
    accounting_periods,
    payment_matching,
    ap_invoices,
    bank_accounts,
    direct_debits,
    debtors,
    creditors,
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
    accruals_provisions,
    chart_of_accounts,
    finance_actions,
    lohn_connector,
    quadriga_connector,
    asset_ledger_connector,
    fibu_connectors,
    iban_lookup,
    credit_debit_memos,
    portal_shop,
    # L3-Connect gap closure
    inventory_counts,
    weighing_tickets,
    warehouse_transfers,
    preparation_lists,
    pick_lists,
    gs1_parser,
    nve,
    webhooks,
    article_extensions,
    nutrient_compositions,
    customer_extensions,
    business_partners,
    messages,
    channel_work_surfaces,
    dms_images,
    sales_shipping_ext,
    master_data,
    charges,
    banken,
    compliance,
    gobd_archiv,
    disposition,
    dokumente,
    vertraege,
    waage,
    zertifikate,
    foerderung,
    marketing,
    labor,
    fuhrpark,
    strecke_speditionen,
    tours,
    sustainability,
    compat,
    modules,
    agrar_contracts,
    agrar_varieties,
    silo,
    agrar_settlements,
    harvest_acceptance,
    rations_optimization,
    quality_protocols,
    daily_prices,
    self_billing,
    nawaro,
    nawaro_raps,
    einkauf_lieferschein,
    einkauf_bestellvorschlag,
    admin_monitoring,
    admin_core,
    data_quality,
    admin_pos,
    admin_devices,
    admin_mobile,
    admin_reporting,
    config_service,
    job_runner,
    controlling,
    training,
    personal,
    analytics,
    commodity_positions,
    position_rules,
    position_overrides,
    batch,
    agents,
    pos_retoure,
    pos_dsfinvk,
)

# Wave 6-9 Process-Kernel-Endpoints (agrar-p0, supplier, wave-7, wave-9)
from app.api.v1.endpoints import (
    agrar_p0,
    supplier_portal,
    reklamation_api,
    price_hedge_api,
    silo_operations_api,
    read_model_snapshots,
    edi_api,
    zertifikate_api,
    ernte_kampagne_api,
)
# Wave 2-19 Process-Kernel Read-Models + Commands
from app.api.v1.endpoints import agent_context_api, finance_read_models, process_kernel_api

# Wave 69 — Knowledge Core
from app.api.v1.endpoints import knowledge_api

# Import domain routers
from app.domains.agrar.api import psm, psm_proplanta
from app.domains.inventory.api import router as inventory_domain_router
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
    batch.router,
    tags=["batch"],
)

api_router.include_router(
    agents.router,
    tags=["neuroassist", "agents"],
)

api_router.include_router(
    channel_work_surfaces.router,
)

api_router.include_router(
    health,
    prefix="/health",
    tags=["health"]
)

api_router.include_router(
    modules.router,
    prefix="/meta",
    tags=["modules", "meta"]
)

api_router.include_router(
    admin_monitoring.router,
    prefix="/admin/monitoring",
    tags=["admin", "monitoring"]
)

api_router.include_router(
    admin_core.router,
    prefix="/admin",
    tags=["admin"]
)

api_router.include_router(
    data_quality.router,
    prefix="/admin",
    tags=["admin", "data-quality"]
)

api_router.include_router(
    admin_pos.router,
    prefix="/admin",
    tags=["admin", "pos", "tse", "dsfinvk"]
)

api_router.include_router(
    admin_devices.router,
    prefix="/admin",
    tags=["admin", "settings", "devices", "output"]
)

api_router.include_router(
    admin_mobile.router,
    prefix="/admin/mobile",
    tags=["admin", "settings", "mobile", "routing", "connectors"]
)

api_router.include_router(
    admin_reporting.router,
    prefix="/admin",
    tags=["admin", "settings", "reporting"]
)

api_router.include_router(
    config_service.router,
    prefix="/config",
    tags=["config", "connectors", "reporting-units", "schedules"]
)

api_router.include_router(
    job_runner.router,
    prefix="/jobs",
    tags=["jobs", "scheduler", "artifacts"]
)

api_router.include_router(
    tenants,
    prefix="/tenants",
    tags=["tenants"]
)

api_router.include_router(
    users,
    prefix="/users",
    tags=["users"]
)

api_router.include_router(
    customers,
    prefix="/crm/customers",
    tags=["crm", "customers"]
)

api_router.include_router(
    crm_reports.router,
    tags=["crm", "reports"]
)

api_router.include_router(
    sales_orders.router,
    prefix="/sales/orders",
    tags=["sales", "orders"]
)

api_router.include_router(
    sales_offers.router,
    prefix="/sales/offers",
    tags=["sales", "offers"]
)

from .endpoints import sales_delivery_notes, branches, pricing, price_lists, sales_credit_notes, sales_reports

api_router.include_router(
    sales_delivery_notes.router,
    tags=["sales", "delivery-notes"]
)

api_router.include_router(
    branches.router,
    tags=["admin", "branches"]
)

api_router.include_router(
    pricing.router,
    tags=["pricing"]
)

api_router.include_router(
    price_lists.router,
    tags=["sales", "pricing", "price-lists"]
)

api_router.include_router(
    sales_credit_notes.router,
    tags=["sales", "credit-notes", "returns"]
)

api_router.include_router(
    sales_reports.router,
    tags=["sales", "reports", "dashboard"]
)

api_router.include_router(
    docflow.router,
    prefix="/docflow",
    tags=["docflow"]
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
    vat_codes.router,
    tags=["finance", "vat-codes"]
)

api_router.include_router(
    audit.router,
    prefix="/audit",
    tags=["audit", "compliance", "gobd"]
)

api_router.include_router(
    export_service.router,
    prefix="/export",
    tags=["export"]
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
    tags=["procurement", "ap", "memos"]
)

api_router.include_router(
    debtors.router,
    prefix="/finance",
    tags=["finance", "debtors"]
)

api_router.include_router(
    creditors.router,
    prefix="/finance",
    tags=["finance", "creditors"]
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
    bank_accounts.router,
    prefix="/finance",
    tags=["finance", "bank-accounts"]
)

api_router.include_router(
    direct_debits.router,
    prefix="/finance",
    tags=["finance", "direct-debits"]
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
    accruals_provisions.router,
    prefix="/finance",
    tags=["finance", "closing", "accruals"]
)

api_router.include_router(
    chart_of_accounts,
    prefix="/finance",
    tags=["finance", "kontenplan", "chart-of-accounts"]
)

api_router.include_router(
    finance_actions.router,
    prefix="/finance",
    tags=["finance", "actions"]
)
api_router.include_router(
    lohn_connector.router,
    prefix="/finance",
    tags=["finance", "lohn", "connectors"]
)
api_router.include_router(
    quadriga_connector.router,
    prefix="/finance",
    tags=["finance", "quadriga", "connectors"]
)
api_router.include_router(
    asset_ledger_connector.router,
    prefix="/finance",
    tags=["finance", "asset-ledger", "connectors"]
)
api_router.include_router(
    fibu_connectors.router,
    prefix="/finance",
    tags=["finance", "fibu-connectors"]
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
    inventory_domain_router,
    prefix="/inventory",
    tags=["inventory"]
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

api_router.include_router(
    analytics.router,
    tags=["analytics", "dashboard"]
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

api_router.include_router(
    agrar_contracts.router,
    prefix="/agrar/contracts",
    tags=["agrar", "contracts"]
)

api_router.include_router(
    agrar_varieties.router,
    prefix="/agrar/varieties",
    tags=["agrar", "varieties", "sorten"]
)

api_router.include_router(
    silo.router,
    prefix="/silo",
    tags=["agrar", "silo"]
)

api_router.include_router(
    agrar_settlements.router,
    prefix="/agrar/settlements",
    tags=["agrar", "settlements", "self-billing"]
)

api_router.include_router(
    harvest_acceptance.router,
    prefix="/agrar/harvest-acceptance",
    tags=["agrar", "harvest", "acceptance", "ernte-annahme"]
)

api_router.include_router(
    quality_protocols.router,
    prefix="/agrar/quality-protocols",
    tags=["agrar", "quality", "protocols", "labor"]
)

api_router.include_router(
    daily_prices.router,
    prefix="/agrar/daily-prices",
    tags=["agrar", "pricing", "daily-prices"]
)

api_router.include_router(
    self_billing.router,
    prefix="/agrar/self-billing",
    tags=["agrar", "self-billing", "invoices", "e-invoice"]
)

api_router.include_router(
    nawaro.router,
    prefix="/agrar/nawaro",
    tags=["agrar", "nawaro"]
)

api_router.include_router(
    nawaro_raps.router,
    prefix="/agrar/nawaro",
    tags=["agrar", "nawaro", "raps"]
)

# Kundenportal
api_router.include_router(
    portal_shop.router,
    prefix="/portal",
    tags=["portal", "shop", "customer"]
)

api_router.include_router(
    portal_feldbuch.router,
    prefix="/portal",
    tags=["portal", "feldbuch"]
)

# Agrar Feldbuch (ERP-intern)
api_router.include_router(
    agrar_feldbuch.router,
    prefix="/agrar",
    tags=["agrar", "feldbuch"]
)

# Agrar Wetter (BrightSky + Open-Meteo Proxy)
api_router.include_router(
    agrar_wetter.router,
    prefix="/agrar",
    tags=["agrar", "wetter"]
)

# Agrar Maschinenpark
api_router.include_router(
    agrar_maschinen.router,
    prefix="/agrar",
    tags=["agrar", "maschinen"]
)

# Rationsoptimierung (Proxy zu Microservice)
api_router.include_router(
    rations_optimization.router,
    prefix="/agrar/rations-optimization",
    tags=["agrar", "futtermittel", "rations-optimization"]
)

# ── L3-Connect Gap Closure Routers ──────────────────────────────

api_router.include_router(
    inventory_counts.router,
    prefix="/inventory/counts",
    tags=["inventory", "counts"]
)

api_router.include_router(
    weighing_tickets.router,
    prefix="/weighing-tickets",
    tags=["logistics", "weighing"]
)

api_router.include_router(
    warehouse_transfers.router,
    prefix="/warehouses/transfers",
    tags=["inventory", "warehouses", "transfers"]
)

api_router.include_router(
    preparation_lists.router,
    prefix="/preparation-lists",
    tags=["inventory", "logistics"]
)

api_router.include_router(
    pick_lists.router,
    prefix="/pick-lists",
    tags=["logistics", "picking"]
)

api_router.include_router(
    gs1_parser.router,
    prefix="/gs1",
    tags=["utility", "barcode"]
)

api_router.include_router(
    nve.router,
    prefix="/nve",
    tags=["logistics", "shipping"]
)

api_router.include_router(
    webhooks.router,
    prefix="/webhooks",
    tags=["system", "integrations"]
)

api_router.include_router(
    article_extensions.router,
    prefix="/articles",
    tags=["inventory", "articles"]
)

api_router.include_router(
    nutrient_compositions.router,
    prefix="/nutrient-compositions",
    tags=["nutrient-compositions", "duengemittel", "composition"]
)

api_router.include_router(
    customer_extensions.router,
    prefix="/crm/customers",
    tags=["crm", "customers"]
)

api_router.include_router(
    business_partners.router,
    prefix="/crm/business-partners",
    tags=["crm", "business-partners"]
)

api_router.include_router(
    messages.router,
    prefix="/messages",
    tags=["communication", "internal"]
)

api_router.include_router(
    dms_images.router,
    prefix="/dms",
    tags=["documents", "dms"]
)

api_router.include_router(
    sales_shipping_ext.router,
    prefix="/sales-shipping",
    tags=["sales", "shipping"]
)

api_router.include_router(
    master_data.router,
    prefix="/master-data",
    tags=["system", "master-data"]
)

# Charges API
api_router.include_router(
    charges.router
)

api_router.include_router(
    banken.router
)

# Compliance API
api_router.include_router(
    compliance.router
)

# GoBD Archiv, E-Rechnung, Audit-Package (Z1/Z2/Z3)
api_router.include_router(
    gobd_archiv.router
)

# Commodity Position Matrix (rules/overrides before positions for route precedence)
api_router.include_router(position_rules.router)
api_router.include_router(position_overrides.router)
api_router.include_router(commodity_positions.router)

# POS Retoure & Checkout
api_router.include_router(
    pos_retoure.router,
    prefix="/pos",
    tags=["pos", "retoure"],
)

# POS DSFinV-K Export (KassenSichV)
api_router.include_router(
    pos_dsfinvk.router,
    prefix="/pos",
    tags=["pos", "dsfinvk"],
)

# Disposition API
api_router.include_router(
    disposition.router
)

# Dokumente API
api_router.include_router(
    dokumente.router
)

# Verträge API
api_router.include_router(
    vertraege.router
)

# Waage API
api_router.include_router(
    waage.router
)

# Zertifikate API
api_router.include_router(
    zertifikate.router
)

# Förderung API
api_router.include_router(
    foerderung.router
)

# Marketing API
api_router.include_router(
    marketing.router
)

# Labor API
api_router.include_router(
    labor.router
)

# Fuhrpark API
api_router.include_router(
    fuhrpark.router
)

# Strecke – Speditionen/Frachttarife API
api_router.include_router(
    strecke_speditionen.router
)

# Tours API
api_router.include_router(
    tours.router
)

# Sustainability runtime API (BVL/Climatiq/FAOSTAT)
api_router.include_router(
    sustainability.router
)

# Compatibility API (path alignment and missing frontend endpoints)
api_router.include_router(
    compat.router
)

api_router.include_router(
    einkauf_lieferschein.router
)

api_router.include_router(
    einkauf_bestellvorschlag.router,
    tags=["einkauf", "bestellvorschlag", "kontrakte", "lager-konten"]
)

api_router.include_router(
    controlling.router,
    tags=["controlling", "kpi", "dashboard"]
)

api_router.include_router(
    training.router,
    tags=["training", "hr", "onboarding"]
)

api_router.include_router(
    personal.router,
    tags=["personal", "hr"]
)

# Wave 6 — Agrar-P0, Supplier-Portal, Silo-Operations, Contract-Pricing
from app.api.v1.endpoints import contract_pricing_api
api_router.include_router(agrar_p0.router)
api_router.include_router(supplier_portal.router)
api_router.include_router(silo_operations_api.router)
api_router.include_router(contract_pricing_api.router)

# Wave 7 — Reklamation, Price-Hedge, Read-Model-Snapshots
api_router.include_router(reklamation_api.router)
api_router.include_router(price_hedge_api.router)
api_router.include_router(read_model_snapshots.router)

# Wave 9 — EDI, Zertifikate, Ernte-Kampagne
api_router.include_router(edi_api.router)
api_router.include_router(zertifikate_api.router)
api_router.include_router(ernte_kampagne_api.router)

# Wave 2-19 — Process-Kernel Finance Read-Models + Commands/Surfacing
api_router.include_router(finance_read_models.router)
api_router.include_router(process_kernel_api.router)
api_router.include_router(agent_context_api.router)

# Wave 69 — Knowledge Core
api_router.include_router(knowledge_api.router, prefix="/knowledge", tags=["knowledge"])
