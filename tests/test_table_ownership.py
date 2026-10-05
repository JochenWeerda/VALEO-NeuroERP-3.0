"""Tests fuer Tabellen-Besitz (P2)."""

from __future__ import annotations

import pytest

from scripts.check_domain_table_ownership import evaluate
from scripts.table_ownership import (
    SCHEMA_TO_DOMAIN,
    classify_table,
    schemas_by_domain,
)


def test_unbekanntes_schema_faellt_durch() -> None:
    verdict = classify_table("domain_nobody", "widgets")
    assert verdict["ok"] is False
    assert verdict["placement"] == "unknown_schema"


def test_native_tabelle_gehoert_dem_schema() -> None:
    verdict = classify_table("domain_crm", "customers")
    assert verdict["ok"] is True
    assert verdict["owner_domain"] == "crm"
    assert verdict["placement"] == "native"


def test_praefix_im_richtigen_schema() -> None:
    verdict = classify_table("domain_agrar", "agrar_duenger")
    assert verdict["ok"] is True
    assert verdict["placement"] == "prefix"


def test_praefix_ohne_legacy_ist_fehler() -> None:
    verdict = classify_table("domain_inventory", "agrar_geheim")
    assert verdict["ok"] is False
    assert verdict["placement"] == "prefix_mismatch"


def test_legacy_agrar_contracts_bleibt_benannt() -> None:
    verdict = classify_table("domain_inventory", "agrar_contracts")
    assert verdict["ok"] is True
    assert verdict["placement"] == "legacy"
    assert "Inventory" in verdict["reason"]


def test_sales_orders_im_crm_ist_legacy_kein_prefix_fehler() -> None:
    verdict = classify_table("domain_crm", "sales_orders")
    assert verdict["ok"] is True
    assert verdict["placement"] == "legacy"


def test_evaluate_weist_unbekanntes_schema_aus() -> None:
    failures, _notes, classified = evaluate({("domain_ghost", "t1")})
    assert classified == 1
    assert any("domain_ghost" in item for item in failures)


def test_evaluate_zaehlt_legacy() -> None:
    locations = {
        ("domain_crm", "customers"),
        ("domain_crm", "business_partners"),
        ("domain_crm", "sales_orders"),
        ("domain_shared", "tenants"),
        ("domain_shared", "users"),
        ("domain_shared", "audit_logs"),
        ("domain_erp", "journal_entries"),
        ("domain_erp", "journal_entry_lines"),
        ("domain_erp", "chart_of_accounts"),
        ("domain_inventory", "articles"),
        ("domain_inventory", "inventory_stock_movements"),
        ("domain_inventory", "inventory_counts"),
        ("domain_einkauf", "bestellungen"),
        ("domain_einkauf", "lieferanten"),
        ("domain_sales", "delivery_notes"),
        ("domain_sales", "sales_credit_notes"),
        ("domain_sales", "sales_returns"),
        ("domain_ops", "ops_wiegungen"),
        ("domain_ops", "ops_chargen"),
        ("domain_ops", "ops_labor_proben"),
        ("domain_docflow", "document_headers"),
        ("domain_docflow", "document_items"),
        ("domain_docflow", "document_artifacts"),
        ("domain_agrar", "agrar_saatgut"),
        ("domain_agrar", "agrar_duenger"),
        ("domain_controlling", "kpi_definitions"),
        ("domain_controlling", "kpi_timeseries"),
    }
    failures, notes, classified = evaluate(locations)
    assert failures == []
    assert classified == len(locations)
    assert any("sales_orders" in note for note in notes)


def test_alle_index_domains_haben_schemas() -> None:
    grouped = schemas_by_domain()
    for domain in (
        "agrar",
        "crm",
        "dms-compliance",
        "finance",
        "hr",
        "inventory",
        "logistics",
        "platform",
        "procurement",
    ):
        assert grouped[domain], domain
    assert "domain_crm" in SCHEMA_TO_DOMAIN
    assert SCHEMA_TO_DOMAIN["domain_ops"] == "inventory"


@pytest.mark.integration
def test_ownership_check_laeuft_gegen_die_db(require_db) -> None:
    from scripts.check_domain_table_ownership import load_locations

    locations = load_locations(
        __import__("os").environ.get(
            "DATABASE_URL",
            "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp",
        )
    )
    failures, notes, classified = evaluate(locations)
    assert failures == [], failures
    assert classified >= 600
    assert notes
