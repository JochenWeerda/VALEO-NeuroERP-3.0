from __future__ import annotations

from app.api.v1.api import api_router


def test_major_gap_closure_routers_are_reachable():
    paths = {getattr(route, "path", "") for route in api_router.routes}

    expected_paths = {
        "/crm/customers/{customer_id}/360",
        "/crm/accounts/{account_id}/hierarchy",
        "/finance/asset-accounting/assets",
        "/finance/budgets",
        "/finance/liquidity/forecast",
        "/logistik/tours",
        "/logistik/freight-cost/calculate",
        "/einkauf/invoice-verification/match",
        "/einkauf/ers/trigger",
        "/einkauf/rfq",
        "/sales/blanket-orders/",
        "/sales/credit-management/customers/{customer_id}/credit-status",
        "/sales/collective-documents/collective-invoice",
        "/contracts",
        "/futtermittel/rohwaren",
        "/futtermittel/rezepte",
        "/compliance/dsgvo/erasure-requests",
        "/compliance/whistleblower/reports",
        "/compliance/lksg/supplier-risk-assessments",
        "/pos/payment-methods",
        "/pos/checkout/preview",
    }

    missing = sorted(expected_paths - paths)
    assert missing == []
