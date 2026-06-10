"""Verify that a freshly migrated DB exposes the required ERP domain structure.

This is intentionally focused: it asserts representative anchor tables plus
columns whose absence previously caused production/test drift after a database
had been stamped beyond an older migration.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


REQUIRED_STRUCTURE: dict[str, tuple[str, ...]] = {
    "domain_shared": ("tenants", "users", "audit_logs"),
    "domain_crm": ("business_partners", "customers", "sales_orders"),
    "domain_erp": (
        "journal_entries",
        "journal_entry_lines",
        "chart_of_accounts",
        "dunning_rules",
        "dunning_notices",
        "payment_runs",
        "payment_run_items",
        "exchange_rates",
    ),
    "domain_inventory": (
        "articles",
        "inventory_stock_movements",
        "inventory_counts",
        "lkw_annahme_queue",
    ),
    "domain_einkauf": ("bestellungen", "lieferanten", "kontrakte"),
    "domain_ops": ("ops_wiegungen", "ops_chargen", "ops_labor_proben"),
    "domain_finance": ("aufbewahrungsfristen", "self_billing_invoices", "dispute_records"),
    "domain_sales": ("delivery_notes", "sales_credit_notes", "sales_returns"),
    "domain_docflow": ("document_headers", "document_items", "document_artifacts"),
    "domain_agrar": ("agrar_saatgut", "agrar_duenger", "nutrient_compositions"),
    "domain_controlling": ("kpi_definitions", "kpi_timeseries", "dashboard_configs"),
}

REQUIRED_COLUMNS: dict[tuple[str, str], tuple[str, ...]] = {
    ("domain_inventory", "agrar_settlements"): ("campaign_id",),
    (
        "domain_erp",
        "chart_of_accounts",
    ): (
        "account_type",
        "category",
        "subcategory",
        "description",
        "is_summary",
        "balance",
        "last_transaction_date",
        "parent_account_id",
        "deleted_at",
    ),
    (
        "domain_hr",
        "time_entries",
    ): (
        "tenant_id",
        "employee_ref",
        "entry_date",
        "hours",
        "entry_type",
        "source",
        "status",
        "version",
    ),
    (
        "domain_hr",
        "shifts",
    ): (
        "tenant_id",
        "shift_date",
        "required_headcount",
        "starts_at",
        "ends_at",
        "status",
    ),
    (
        "domain_inventory",
        "drying_rule_sets",
    ): (
        "tenant_id",
        "crop_code",
        "version",
        "method",
        "base_moisture_pct",
        "fee_basis",
    ),
}


def main() -> None:
    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp",
    )
    engine = create_engine(database_url)
    failures: list[str] = []

    with engine.begin() as conn:
        for schema, tables in REQUIRED_STRUCTURE.items():
            present = {
                row[0]
                for row in conn.execute(
                    text(
                        """
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = :schema
                        """
                    ),
                    {"schema": schema},
                ).fetchall()
            }
            missing = [table for table in tables if table not in present]
            if missing:
                failures.append(f"{schema}: missing {', '.join(missing)}")

        for (schema, table), columns in REQUIRED_COLUMNS.items():
            present = {
                row[0]
                for row in conn.execute(
                    text(
                        """
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_schema = :schema
                          AND table_name = :table
                        """
                    ),
                    {"schema": schema, "table": table},
                ).fetchall()
            }
            missing = [column for column in columns if column not in present]
            if missing:
                failures.append(
                    f"{schema}.{table}: missing columns {', '.join(missing)}"
                )

    engine.dispose()

    if failures:
        raise SystemExit("Required ERP domain structure missing:\n- " + "\n- ".join(failures))

    print("Required ERP domain structure OK.")


if __name__ == "__main__":
    main()
