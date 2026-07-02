"""pricing: staffelrabatte <-> artikel als many-to-many

Preistabellen/Staffelrabatte sollen wie im Referenz-ERP (Tabellen-Nr.-Preistabelle,
je Artikel referenzierbar) mit mehreren Artikeln verknuepft werden koennen, und ein
Artikel soll umgekehrt mehreren Staffeln zugeordnet sein koennen. Bisher gab es nur
die 1:1-Spalte `artikel_id` auf `staffelrabatte`.

Revision ID: pricing_staffelrabatt_artikel_m2m_20260702
Revises: pricing_staffelrabatte_20260701
Create Date: 2026-07-02
"""

from __future__ import annotations

from alembic import op

revision = "pricing_staffelrabatt_artikel_m2m_20260702"
down_revision = "pricing_staffelrabatte_20260701"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_pricing.staffelrabatt_artikel (
            staffelrabatt_id  VARCHAR(36)  NOT NULL REFERENCES domain_pricing.staffelrabatte(id) ON DELETE CASCADE,
            artikel_id        VARCHAR(36)  NOT NULL,
            tenant_id         VARCHAR(64)  NOT NULL,
            created_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            PRIMARY KEY (staffelrabatt_id, artikel_id)
        )
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_staffelrabatt_artikel_tenant_artikel
            ON domain_pricing.staffelrabatt_artikel (tenant_id, artikel_id)
    """)
    # Backfill: bestehende 1:1-Zuordnung aus der alten artikel_id-Spalte übernehmen.
    op.execute("""
        INSERT INTO domain_pricing.staffelrabatt_artikel (staffelrabatt_id, artikel_id, tenant_id)
        SELECT id, artikel_id, tenant_id
        FROM domain_pricing.staffelrabatte
        WHERE artikel_id IS NOT NULL
        ON CONFLICT DO NOTHING
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_pricing.staffelrabatt_artikel")
