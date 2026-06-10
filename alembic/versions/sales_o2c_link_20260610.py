"""sales O2C-Link — Auftrag→Lieferschein-Verknüpfung (DOM-SALES-004.1)

Schließt die Modelllücke der O2C-Kette: delivery_notes erhält einen optionalen
Bezug auf den Kundenauftrag (sales_orders). Additiv, nullable — bestehende
Lieferscheine bleiben unberührt.

Revision ID: sales_o2c_link_20260610
Revises: crm_ownership_log_20260610
Create Date: 2026-06-10
"""

from __future__ import annotations

from alembic import op

revision = "sales_o2c_link_20260610"
down_revision = "crm_ownership_log_20260610"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE domain_sales.delivery_notes ADD COLUMN IF NOT EXISTS sales_order_id UUID")
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_delivery_notes_sales_order "
        "ON domain_sales.delivery_notes (sales_order_id)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_sales.ix_delivery_notes_sales_order")
    op.execute("ALTER TABLE domain_sales.delivery_notes DROP COLUMN IF EXISTS sales_order_id")
