"""Tests fuer scripts/generate_architecture_index.py und Prefix-Regeln."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.generate_architecture_index import (
    PREFIX_CONFIG,
    build_index,
    endpoint_domain,
    get_rules,
    load_prefix_rules,
    route_domain,
    service_domain,
    validate_complete,
)

REPO = Path(__file__).resolve().parents[1]


@pytest.mark.unit
def test_prefix_config_exists() -> None:
    assert PREFIX_CONFIG.exists(), "config/architecture-domain-prefixes.yaml fehlt"


@pytest.mark.unit
def test_prefix_rules_load_domains() -> None:
    rules = load_prefix_rules()
    assert "crm" in rules.route_segment_to_domain.values()
    assert rules.service_prefixes
    assert rules.endpoint_prefixes


@pytest.mark.unit
def test_route_domain_segment_and_module_fallback() -> None:
    assert route_domain("crm/kunden") == "crm"
    assert route_domain("agribusiness/farmers", "@/pages/agribusiness/farmers") == "agrar"
    assert route_domain("", "") == "platform"


@pytest.mark.unit
def test_service_domain_prefix_and_exact() -> None:
    assert service_domain("crm_core_service") == "crm"
    assert service_domain("einkauf_compat_service") == "procurement"
    assert service_domain("kaeufergruppe") == "crm"


@pytest.mark.unit
def test_endpoint_domain_prefix_and_exact() -> None:
    assert endpoint_domain("sales_orders") == "crm"
    assert endpoint_domain("accounts") == "finance"
    assert endpoint_domain("supply_chain") == "agrar"
    assert endpoint_domain("vertraege") == "agrar"


@pytest.mark.unit
def test_build_index_mapping_complete() -> None:
    index = build_index()
    errors = validate_complete(index)
    assert not errors, errors
    stats = index["mapping_stats"]
    assert stats["frontend_routes_mapped"] == stats["frontend_routes_total"]
    assert stats["backend_services_mapped"] == stats["backend_services_total"]
    assert stats["backend_endpoints_mapped"] == stats["backend_endpoints_total"]
    assert index["unmapped"]["frontend_routes"] == []
    assert index["unmapped"]["backend_services"] == []
    assert index["unmapped"]["backend_endpoints"] == []


@pytest.mark.unit
def test_build_index_has_logistics_and_hr_domains() -> None:
    index = build_index()
    assert "logistics" in index["domains"]
    assert "hr" in index["domains"]
