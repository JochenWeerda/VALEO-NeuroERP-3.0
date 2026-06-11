"""Ensure finance_erechnungen for procurement three-way match.

Revision ID: proc_three_way_inv_20260611
Revises: con_settlement_storno_20260611
"""

from alembic import op


revision = "proc_three_way_inv_20260611"
down_revision = "con_settlement_storno_20260611"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.finance_erechnungen (
            id VARCHAR(36) PRIMARY KEY,
            tenant_id VARCHAR(36) NOT NULL,
            rechnungsnummer VARCHAR(50) NOT NULL,
            rechnungsdatum DATE NOT NULL,
            leistungsdatum DATE,
            faelligkeitsdatum DATE NOT NULL,
            lieferant_name VARCHAR(200) NOT NULL,
            lieferant_adresse VARCHAR(500),
            lieferant_ust_id VARCHAR(20),
            lieferant_gln VARCHAR(20),
            rechnungssteller_name VARCHAR(200) NOT NULL,
            rechnungssteller_adresse VARCHAR(500),
            rechnungssteller_ust_id VARCHAR(20),
            gesamt_netto NUMERIC(10, 2) NOT NULL DEFAULT 0,
            gesamt_mwst NUMERIC(10, 2) NOT NULL DEFAULT 0,
            gesamt_brutto NUMERIC(10, 2) NOT NULL DEFAULT 0,
            zugeordneter_auftrag VARCHAR(50),
            zugeordneter_lieferschein VARCHAR(50),
            status VARCHAR(20) DEFAULT 'ERSTELLT',
            checksum_sha256 VARCHAR(64),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ
        );
        CREATE INDEX IF NOT EXISTS ix_finance_erechnungen_tenant_po
            ON public.finance_erechnungen (tenant_id, zugeordneter_auftrag);
        """
    )


def downgrade() -> None:
    pass
