"""DOM-POS-004 — POS Tagesabschluss Lifecycle Tabellen

Revision ID: pos_tagesabschluss_lifecycle_20260623
Revises: feed_produktion_lifecycle_20260623
Create Date: 2026-06-23
"""
from alembic import op
import sqlalchemy as sa

revision = "pos_tagesabschluss_lifecycle_20260623"
down_revision = "feed_produktion_lifecycle_20260623"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_pos")

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_pos.pos_tagesabschluesse (
            id                      UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            tenant_id               TEXT NOT NULL,
            kasse_id                TEXT NOT NULL,
            datum                   TEXT NOT NULL,
            status                  TEXT NOT NULL DEFAULT 'OFFEN',
            z_bon_nr                TEXT,
            tse_signatur            TEXT,
            tse_serial              TEXT,
            dsfinvk_export_pfad     TEXT,
            umsatz_brutto_eur       NUMERIC(14,2),
            fehler_grund            TEXT,
            operator                TEXT NOT NULL DEFAULT 'system',
            created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at              TIMESTAMPTZ,
            UNIQUE (tenant_id, kasse_id, datum)
        )
    """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS domain_pos.pos_tagesabschluss_log (
            id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            abschluss_id    UUID NOT NULL,
            tenant_id       TEXT NOT NULL,
            old_status      TEXT NOT NULL DEFAULT '',
            new_status      TEXT NOT NULL,
            operator        TEXT NOT NULL DEFAULT 'system',
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_pos.pos_tagesabschluss_log")
    op.execute("DROP TABLE IF EXISTS domain_pos.pos_tagesabschluesse")
