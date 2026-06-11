"""DOM-SALES-004.4 — Lieferungs-Storno (Grund am Lieferschein).

Revision ID: sales_delivery_storno_20260611
Revises: con_settlement_storno_20260611

Ergänzt domain_sales.delivery_notes um ``storno_grund`` (revisionssicherer Grund;
der Storno selbst nutzt das vorhandene ``status``='storniert'). Stornierte Liefer-
scheine zählen nicht mehr als geliefert (Auftrag-↔-Lieferschein-Match).
Idempotent (``ADD COLUMN IF NOT EXISTS``).
"""

from typing import Sequence, Union

from alembic import op

revision: str = "sales_delivery_storno_20260611"
down_revision: Union[str, Sequence[str], None] = "con_settlement_storno_20260611"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE domain_sales.delivery_notes ADD COLUMN IF NOT EXISTS storno_grund TEXT;"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE domain_sales.delivery_notes DROP COLUMN IF EXISTS storno_grund;"
    )
