"""Procurement match follow-up actions (append-only).

Revision ID: proc_follow_up_20260611
Revises: proc_three_way_inv_20260611
"""

from alembic import op


revision = "proc_follow_up_20260611"
down_revision = "proc_three_way_inv_20260611"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute(
        f"""
        CREATE TABLE IF NOT EXISTS domain_einkauf.procurement_follow_up (
            id VARCHAR PRIMARY KEY,
            tenant_id VARCHAR NOT NULL,
            bestellnummer VARCHAR(64) NOT NULL,
            action_type VARCHAR(32) NOT NULL,
            ausnahme_code VARCHAR(64),
            grund TEXT NOT NULL,
            eskalationsstufe INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            created_by TEXT,
            CONSTRAINT procurement_follow_up_action_ck
                CHECK (action_type IN ('nachforderung', 'reklamation', 'eskalation', 'freigabe')),
            CONSTRAINT procurement_follow_up_grund_ck CHECK (char_length(trim(grund)) > 0)
        );
        CREATE INDEX IF NOT EXISTS procurement_follow_up_tenant_po_idx
            ON domain_einkauf.procurement_follow_up (tenant_id, bestellnummer, created_at DESC);
        """
    )


def downgrade() -> None:
    pass
