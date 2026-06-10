"""Verify representative table ownership across ERP domain schemas.

This script does not attempt a full semantic proof. It enforces:
1. Exact ownership for selected anchor tables.
2. Prefix-based ownership for tables whose naming already encodes a domain.
3. Documented tolerated legacy placements, so drift becomes explicit.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

EXACT_TABLE_OWNERSHIP: dict[str, tuple[str, ...]] = {
    "domain_shared": ("tenants", "users", "audit_logs"),
    "domain_crm": ("business_partners", "customers"),
    "domain_erp": ("journal_entries", "journal_entry_lines", "chart_of_accounts"),
    "domain_inventory": ("articles", "inventory_stock_movements", "inventory_counts"),
    "domain_einkauf": ("bestellungen", "lieferanten"),
    "domain_sales": ("delivery_notes", "sales_credit_notes", "sales_returns"),
    "domain_ops": ("ops_wiegungen", "ops_chargen", "ops_labor_proben"),
    "domain_docflow": ("document_headers", "document_items", "document_artifacts"),
    "domain_agrar": ("agrar_saatgut", "agrar_duenger"),
    "domain_controlling": ("kpi_definitions", "kpi_timeseries"),
}

PREFIX_SCHEMA_RULES: dict[str, str] = {
    "ops_": "domain_ops",
    "agrar_": "domain_agrar",
    "sales_": "domain_sales",
    "kpi_": "domain_controlling",
    "document_": "domain_docflow",
}

TOLERATED_LEGACY_LOCATIONS: dict[tuple[str, str], str] = {
    ("domain_inventory", "lkw_annahme_queue"): "Annahme-Queue liegt historisch bei Inventory.",
    ("domain_einkauf", "kontrakte"): "Kontrakte liegen historisch im Einkaufsschema.",
    ("domain_crm", "sales_offers"): "Sales-Angebote liegen historisch im CRM-Schema.",
    ("domain_crm", "sales_offer_items"): "Sales-Angebotspositionen liegen historisch im CRM-Schema.",
    ("domain_crm", "sales_orders"): "Sales-Auftraege liegen historisch im CRM-Schema.",
    ("domain_crm", "sales_order_items"): "Sales-Auftragspositionen liegen historisch im CRM-Schema.",
    ("domain_finance", "sales_order"): "FIBU-Referenzobjekt sales_order liegt historisch in domain_finance.",
    ("domain_inventory", "agrar_contracts"): "Agrar-Kontrakte liegen historisch im Inventory-Schema.",
    ("domain_inventory", "agrar_contract_allocations"): "Agrar-Kontraktallokationen liegen historisch im Inventory-Schema.",
    ("domain_inventory", "agrar_settlements"): "Agrar-Abrechnungen liegen historisch im Inventory-Schema.",
    ("domain_inventory", "agrar_settlement_deductions"): "Agrar-Abzuege liegen historisch im Inventory-Schema.",
    ("domain_shared", "agrar_sorten"): "Agrar-Sorten liegen historisch im Shared-Schema.",
}


def main() -> None:
    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp",
    )
    engine = create_engine(database_url)
    failures: list[str] = []
    notes: list[str] = []

    with engine.begin() as conn:
        rows = conn.execute(
            text(
                """
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_type = 'BASE TABLE'
                  AND table_schema LIKE 'domain_%'
                ORDER BY table_schema, table_name
                """
            )
        ).fetchall()

    engine.dispose()

    locations = {(row[0], row[1]) for row in rows}
    schema_by_table: dict[str, set[str]] = {}
    for schema, table in locations:
        schema_by_table.setdefault(table, set()).add(schema)

    for schema, tables in EXACT_TABLE_OWNERSHIP.items():
        for table in tables:
            if (schema, table) not in locations:
                actual_schemas = sorted(schema_by_table.get(table, set()))
                failures.append(
                    f"{table}: expected {schema}, found {', '.join(actual_schemas) if actual_schemas else 'missing'}"
                )

    for schema, table in sorted(TOLERATED_LEGACY_LOCATIONS):
        if (schema, table) in locations:
            notes.append(f"{schema}.{table}: {TOLERATED_LEGACY_LOCATIONS[(schema, table)]}")

    for schema, table in locations:
        if (schema, table) in TOLERATED_LEGACY_LOCATIONS:
            continue
        for prefix, expected_schema in PREFIX_SCHEMA_RULES.items():
            if table.startswith(prefix) and schema != expected_schema:
                failures.append(
                    f"{schema}.{table}: prefix '{prefix}' expects ownership in {expected_schema}"
                )

    if notes:
        print("Documented legacy placements:")
        for note in notes:
            print(f"- {note}")

    if failures:
        raise SystemExit("Domain table ownership drift detected:\n- " + "\n- ".join(sorted(failures)))

    print("Domain table ownership OK.")


if __name__ == "__main__":
    main()
