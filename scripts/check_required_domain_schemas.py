"""Verify that a freshly migrated DB exposes the required ERP domain structure.

This is intentionally lightweight: it does not assert every table, only the
core schemas and representative anchor tables that prove the multi-domain ERP
layout is present after `alembic upgrade head`.
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
    "domain_inventory": ("articles", "stock_movements", "inventory_counts", "lkw_annahme_queue"),
    "domain_einkauf": ("bestellungen", "lieferanten", "kontrakte"),
    "domain_ops": ("ops_wiegungen", "ops_chargen", "ops_labor_proben"),
    "domain_finance": ("aufbewahrungsfristen", "self_billing_invoices", "dispute_records"),
    "domain_sales": ("delivery_notes", "sales_credit_notes", "sales_returns"),
    "domain_docflow": ("document_headers", "document_items", "document_artifacts"),
    "domain_agrar": ("agrar_saatgut", "agrar_duenger", "nutrient_compositions"),
    "domain_controlling": ("kpi_definitions", "kpi_timeseries", "dashboard_configs"),
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

    engine.dispose()

    if failures:
        raise SystemExit("Required ERP domain structure missing:\n- " + "\n- ".join(failures))

    print("Required ERP domain structure OK.")


if __name__ == "__main__":
    main()
