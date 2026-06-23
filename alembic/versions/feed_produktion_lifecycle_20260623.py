"""DOM-FEED-PROD-004 — Mischfutter Produktionsauftrag, Rezeptur, QS-Log

Revision ID: feed_produktion_lifecycle_20260623
Revises: kontrakt_lifecycle_fixing_20260623
Create Date: 2026-06-23
"""
from alembic import op
import sqlalchemy as sa

revision = "feed_produktion_lifecycle_20260623"
down_revision = "kontrakt_lifecycle_fixing_20260623"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_futtermittel")

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_futtermittel.feed_rezepturen (
            id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            rezeptur_nr     TEXT NOT NULL,
            artikel_id      TEXT NOT NULL,
            bezeichnung     TEXT NOT NULL DEFAULT '',
            version         INT NOT NULL DEFAULT 1,
            status          TEXT NOT NULL DEFAULT 'ENTWURF',
            operator        TEXT NOT NULL DEFAULT 'system',
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_futtermittel.feed_rezeptur_positionen (
            id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            rezeptur_id     UUID NOT NULL,
            tenant_id       TEXT NOT NULL,
            rohware_id      TEXT NOT NULL,
            anteil_pct      NUMERIC(7,4) NOT NULL,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_futtermittel.feed_produktionsauftraege (
            id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            tenant_id       TEXT NOT NULL,
            rezeptur_id     UUID NOT NULL,
            soll_menge_kg   NUMERIC(12,3) NOT NULL,
            ist_menge_kg    NUMERIC(12,3),
            geplant_datum   TEXT NOT NULL,
            charge_nr       TEXT NOT NULL,
            status          TEXT NOT NULL DEFAULT 'GEPLANT',
            qs_befund       TEXT NOT NULL DEFAULT '',
            operator        TEXT NOT NULL DEFAULT 'system',
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_futtermittel.feed_produktion_log (
            id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            auftrag_id      UUID NOT NULL,
            tenant_id       TEXT NOT NULL,
            old_status      TEXT NOT NULL DEFAULT '',
            new_status      TEXT NOT NULL,
            operator        TEXT NOT NULL DEFAULT 'system',
            qs_befund       TEXT NOT NULL DEFAULT '',
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_futtermittel.feed_produktion_log")
    op.execute("DROP TABLE IF EXISTS domain_futtermittel.feed_produktionsauftraege")
    op.execute("DROP TABLE IF EXISTS domain_futtermittel.feed_rezeptur_positionen")
    op.execute("DROP TABLE IF EXISTS domain_futtermittel.feed_rezepturen")
