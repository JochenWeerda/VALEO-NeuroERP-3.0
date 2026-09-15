"""UIX-091: Prozessketten-Katalog und Readiness-Warnung.

Reine Unit-Tests: pytest tests/test_uix091_process_chain_contract.py --noconftest -p no:cacheprovider --no-cov -q -o addopts=""
"""
from __future__ import annotations

import pytest

from app.api.v1.endpoints.mask_screen_definition import _check_readiness
from app.core.process_chains import attach_process_chain, membership_for, needs_process_chain
from app.core.screen_definitions import get_screen_definition, get_screen_list_route

pytestmark = pytest.mark.unit


def test_delivery_note_gets_verkauf_chain_and_catalog_routes():
    sd = get_screen_definition("sales/delivery-note")
    assert sd is not None
    assert sd["processChain"] == {"chainId": "k2_verkauf", "stepKey": "lieferschein"}
    verkauf = sd["processChains"]["k2_verkauf"]
    lieferschein = next(step for step in verkauf["steps"] if step["key"] == "lieferschein")
    assert lieferschein["routePath"] == get_screen_list_route("sales/delivery-note")
    auftrag = next(step for step in verkauf["steps"] if step["key"] == "auftrag")
    assert auftrag["routePath"] == "/verkauf/auftraege"


def test_purchase_order_gets_einkauf_chain():
    sd = get_screen_definition("einkauf/purchase-order")
    assert sd is not None
    assert sd["processChain"] == {"chainId": "k3_einkauf", "stepKey": "bestellung"}


def test_explicit_process_chain_is_not_overwritten():
    definition = {"id": "sales/delivery-note", "domain": "sales", "mode": "detail"}
    definition["processChain"] = {"chainId": "custom", "stepKey": "x"}
    attach_process_chain(definition, get_screen_list_route)
    assert definition["processChain"] == {"chainId": "custom", "stepKey": "x"}
    assert "k2_verkauf" in definition["processChains"]


def test_membership_unknown_screen_is_none():
    assert membership_for("workspace/einkauf") is None


def test_readiness_warns_when_beleg_mask_has_no_chain():
    screen = {
        "schemaVersion": 1,
        "id": "einkauf/supplier",
        "domain": "einkauf",
        "mode": "detail",
        "title": "Lieferant",
        "adapter": {"type": "native", "temporary": False},
        "noWorkflowReason": "Stammdaten",
        "layout": {
            "floorplan": "objectPage",
            "density": "compact",
            "contextRail": "combined",
            "tableProfile": "standard",
        },
        "dataSources": [{"key": "entity", "endpoint": "/api/v1/einkauf/lieferanten/{entity_id}"}],
        "agentContract": {
            "businessPurpose": "Lieferantenstamm",
            "testSelectors": {"screenRoot": '[data-testid="screen-einkauf/supplier"]'},
        },
    }
    assert needs_process_chain(screen) is True
    report = _check_readiness(screen)
    assert report["generatorReady"] is True
    assert any("missing_process_chain" in warning for warning in report["warnings"])


def test_order_confirmation_joins_einkauf_chain():
    sd = get_screen_definition("einkauf/auftragsbestaetigung")
    assert sd is not None
    assert sd["processChain"] == {"chainId": "k3_einkauf", "stepKey": "bestaetigung"}


def test_supplier_gets_explicit_non_document_reason():
    sd = get_screen_definition("einkauf/supplier")
    assert sd is not None
    assert "processChain" not in sd
    assert sd["noProcessChainReason"] == "Stammdatenmaske ohne Belegkette"
    report = _check_readiness(sd)
    gate = next(item for item in report["gates"] if item["gate"] == "missing_process_chain")
    assert gate["passed"] is True


def test_all_document_domain_screens_have_chain_or_reason():
    from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS

    unclassified: list[str] = []
    for screen_id in SCREEN_DEFINITION_BUILDERS:
        sd = get_screen_definition(screen_id)
        if sd is None or not needs_process_chain(sd):
            continue
        has_chain = bool((sd.get("processChain") or {}).get("chainId"))
        has_reason = bool(str(sd.get("noProcessChainReason") or "").strip())
        if not has_chain and not has_reason:
            unclassified.append(screen_id)
    assert unclassified == []


def test_readiness_accepts_no_process_chain_reason():
    screen = {
        "schemaVersion": 1,
        "id": "finance/debitor",
        "domain": "finance",
        "mode": "detail",
        "title": "Debitor",
        "adapter": {"type": "native", "temporary": False},
        "noWorkflowReason": "Stammdaten",
        "noProcessChainReason": "Stammdatenmaske ohne Belegkette",
        "layout": {
            "floorplan": "objectPage",
            "density": "compact",
            "contextRail": "combined",
            "tableProfile": "financial",
        },
        "dataSources": [{"key": "entity", "endpoint": "/api/v1/finance/debitoren/{entity_id}"}],
        "agentContract": {
            "businessPurpose": "Debitorenstamm",
            "testSelectors": {"screenRoot": '[data-testid="screen-finance/debitor"]'},
        },
    }
    report = _check_readiness(screen)
    assert report["generatorReady"] is True
    gate = next(item for item in report["gates"] if item["gate"] == "missing_process_chain")
    assert gate["passed"] is True
    sd = get_screen_definition("sales/delivery-note")
    assert sd is not None
    report = _check_readiness(sd)
    gate = next(item for item in report["gates"] if item["gate"] == "missing_process_chain")
    assert gate["passed"] is True
