"""DOM-CON-004.4 — Settlement-Übergabe + Storno (Bewegungs-Felder).

Revision ID: con_settlement_storno_20260611
Revises: con_reminder_20260611

Ergänzt domain_ops.kon_contract_movement um Settlement-/Storno-Felder:
- ``settled_at``  — Zeitpunkt der Abrechnungs-Übergabe (zusätzlich zu is_invoiced/invoice_no).
- ``is_storniert``/``storno_grund`` — stornierte Bewegung (zählt nicht mehr als abgerufen).

Idempotent (``ADD COLUMN IF NOT EXISTS``).
"""

from typing import Sequence, Union

from alembic import op

revision: str = "con_settlement_storno_20260611"
down_revision: Union[str, Sequence[str], None] = "con_reminder_20260611"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE domain_ops.kon_contract_movement "
        "ADD COLUMN IF NOT EXISTS settled_at TIMESTAMPTZ, "
        "ADD COLUMN IF NOT EXISTS is_storniert BOOLEAN NOT NULL DEFAULT false, "
        "ADD COLUMN IF NOT EXISTS storno_grund TEXT;"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE domain_ops.kon_contract_movement "
        "DROP COLUMN IF EXISTS storno_grund, "
        "DROP COLUMN IF EXISTS is_storniert, "
        "DROP COLUMN IF EXISTS settled_at;"
    )
