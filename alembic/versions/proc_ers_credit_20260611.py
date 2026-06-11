"""Procurement ERS credit notes (Gutschriftsverfahren).

Revision ID: proc_ers_credit_20260611
Revises: proc_follow_up_20260611
"""

from alembic import op


revision = "proc_ers_credit_20260611"
down_revision = "proc_follow_up_20260611"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_einkauf.procurement_ers_credits (
            id VARCHAR(36) PRIMARY KEY,
            tenant_id VARCHAR(36) NOT NULL,
            bestellnummer VARCHAR(64) NOT NULL,
            gutschrift_nummer VARCHAR(50) NOT NULL,
            betrag_netto NUMERIC(12, 2) NOT NULL,
            grund TEXT NOT NULL,
            ausnahme_code VARCHAR(64),
            status VARCHAR(20) NOT NULL DEFAULT 'entwurf',
            positionen_json JSONB,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            created_by TEXT,
            CONSTRAINT procurement_ers_credits_grund_ck CHECK (char_length(trim(grund)) > 0),
            CONSTRAINT procurement_ers_credits_betrag_ck CHECK (betrag_netto > 0)
        );
        CREATE UNIQUE INDEX IF NOT EXISTS procurement_ers_credits_tenant_nr_uq
            ON domain_einkauf.procurement_ers_credits (tenant_id, gutschrift_nummer);
        CREATE INDEX IF NOT EXISTS procurement_ers_credits_tenant_po_idx
            ON domain_einkauf.procurement_ers_credits (tenant_id, bestellnummer, created_at DESC);
        """
    )


def downgrade() -> None:
    pass
