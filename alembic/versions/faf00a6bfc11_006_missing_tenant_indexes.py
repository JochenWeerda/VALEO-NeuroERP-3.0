"""006 missing tenant indexes

Revision ID: faf00a6bfc11
Revises: streckengeschaefte_table_merge_20260424
Create Date: 2026-05-12 12:07:56.050379

HINWEIS: Autogenerate hat ~30 drop_table-Operationen vorgeschlagen, weil
Tabellen in der DB existieren, die nicht in den SQLAlchemy-Modellen registriert
sind (z.B. kunden*, crm_*, buchungen, translations, workflow_*).
Diese werden hier NICHT gedroppt — sie sind intentional in der DB und werden
über andere Pfade verwaltet.

Die Composite-Indexes für domain_sales / domain_inventory / domain_erp werden
über den SQL-Runner verwaltet:
  migrations/sql/erp/006_missing_tenant_indexes.sql
  → pnpm migrate:erp-finanz  (oder tools/migration/run_sql_migration.ts direkt)

Diese Alembic-Revision ist daher ein bewusster No-Op und dient nur dazu,
die Revisionskette lückenlos zu halten.
"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = 'faf00a6bfc11'
down_revision: Union[str, None] = 'streckengeschaefte_table_merge_20260424'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Indexes werden über migrations/sql/erp/006_missing_tenant_indexes.sql verwaltet.
    pass


def downgrade() -> None:
    pass
