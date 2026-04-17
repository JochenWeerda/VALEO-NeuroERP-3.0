"""domain_crm.customers — pg_trgm GIN-Indizes fuer schnelle Typeahead-Suche

Revision ID: crm_customers_search_index_20260414
Revises: ensure_finance_api_tables_20260413
Create Date: 2026-04-14
"""

from typing import Sequence, Union

from alembic import op


revision: str = "crm_customers_search_index_20260414"
down_revision: Union[str, None] = "ensure_finance_api_tables_20260413"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_customers_company_name_trgm "
        "ON domain_crm.customers USING gin (company_name gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_customers_customer_number_trgm "
        "ON domain_crm.customers USING gin (customer_number gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_customers_updated_at "
        "ON domain_crm.customers (updated_at DESC)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_crm.ix_customers_updated_at")
    op.execute("DROP INDEX IF EXISTS domain_crm.ix_customers_customer_number_trgm")
    op.execute("DROP INDEX IF EXISTS domain_crm.ix_customers_company_name_trgm")
