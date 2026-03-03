"""journal_entries: Spalte currency ergänzen

Revision ID: b0c1d2e3f4a5
Revises: a9b0c1d2e3f4
Create Date: 2026-03-03

Fügt domain_erp.journal_entries.currency hinzu, falls fehlend (Bulk-Import,
OP-Settle, Vorlagen, Bankabgleich nutzen die Spalte).
"""
from __future__ import annotations

from alembic import op
from sqlalchemy import text

revision = "b0c1d2e3f4a5"
down_revision = "a9b0c1d2e3f4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    r = conn.execute(text("""
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'domain_erp' AND table_name = 'journal_entries' AND column_name = 'currency'
    """))
    if r.scalar() is None:
        op.execute(text("""
            ALTER TABLE domain_erp.journal_entries
            ADD COLUMN currency VARCHAR(3) NULL DEFAULT 'EUR'
        """))


def downgrade() -> None:
    op.execute(text("ALTER TABLE domain_erp.journal_entries DROP COLUMN IF EXISTS currency"))
