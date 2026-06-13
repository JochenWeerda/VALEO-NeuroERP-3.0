"""Einkauf 3-Wege-Match: domain_einkauf.invoice_verification Alembic migration.

Revision ID: einkauf_3wm_invoice_verification_20260613
Revises: feed_chain_quality_lot_20260613
Create Date: 2026-06-13
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "einkauf_3wm_invoice_verification_20260613"
down_revision = "feed_chain_quality_lot_20260613"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_einkauf")
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_einkauf.invoice_verification (
            id                BIGSERIAL PRIMARY KEY,
            po_id             TEXT NOT NULL,
            gr_id             TEXT NOT NULL,
            invoice_id        TEXT NOT NULL,
            match_status      TEXT NOT NULL DEFAULT 'OFFEN',
            po_amount         NUMERIC(18,4),
            gr_amount         NUMERIC(18,4),
            invoice_amount    NUMERIC(18,4),
            variance_amount   NUMERIC(18,4),
            variance_percent  NUMERIC(10,4),
            tolerance_percent NUMERIC(10,4) DEFAULT 2.0,
            tenant_id         TEXT,
            created_at        TIMESTAMPTZ DEFAULT NOW(),
            verified_at       TIMESTAMPTZ,
            verified_by       TEXT,
            comment           TEXT
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_inv_verif_tenant_status
        ON domain_einkauf.invoice_verification (tenant_id, match_status)
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_inv_verif_po_gr_invoice
        ON domain_einkauf.invoice_verification (po_id, gr_id, invoice_id)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_einkauf.invoice_verification")
